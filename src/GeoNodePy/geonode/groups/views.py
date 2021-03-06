from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required

from geonode.groups.forms import GroupInviteForm, GroupForm, GroupUpdateForm
from geonode.groups.forms import GroupMapForm, GroupLayerForm

from geonode.groups.models import Group, GroupInvitation

from geonode.maps.models import Layer, Map, GroupLayer, GroupMap

from actstream import action


def group_list(request):
    ctx = {
        "object_list": Group.objects.exclude(access="private"),
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_list.html", ctx)


@login_required
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            group.join(request.user, role="manager")
            if group.access != "private":
                action.send(request.user, verb="created", target=group)
            return redirect("group_detail", group.slug)
    else:
        form = GroupForm()
    
    return render_to_response("groups/group_create.html", {
        "form": form,
    }, context_instance=RequestContext(request))


@login_required
def group_update(request, slug):
    group = Group.objects.get(slug=slug)
    if not group.user_is_role(request.user, role="manager"):
        return HttpResponseForbidden()
    
    if request.method == "POST":
        form = GroupUpdateForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            if group.access != "private":
                action.send(request.user, verb="updated", target=group)
            return redirect("group_detail", group.slug)
    else:
        form = GroupForm(instance=group)
    
    return render_to_response("groups/group_update.html", {
        "form": form,
    }, context_instance=RequestContext(request))


def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    if not group.can_view(request.user):
        raise Http404()
        
    maps = GroupMap.maps_for_group(group)
    layers = GroupLayer.layers_for_group(group)
    
    if request.method == "POST":
        if group.user_is_member(request.user):
            group.leave(request.user)
            if group.access != "private":
                action.send(request.user, verb="left", target=group)
        else:
            group.join(request.user)
            if group.access != "private":
                action.send(request.user, verb="joined", target=group)
                
        return redirect("group_detail", group.slug)
        
    ctx = {
        "object": group,
        "maps": maps,
        "layers": layers,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_detail.html", ctx)


def group_members(request, slug):
    group = get_object_or_404(Group, slug=slug)
    ctx = {}
    
    if not group.can_view(request.user):
        raise Http404()
    
    if group.access in ["public-invite", "private"] and group.user_is_role(request.user, "manager"):
        ctx["invite_form"] = GroupInviteForm()
    
    ctx.update({
        "object": group,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
    })
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_members.html", ctx)


@require_POST
@login_required
def group_join(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    if group.access == "private":
        raise Http404()
    
    if group.user_is_member(request.user):
        return redirect("group_members", slug=group.slug)
    else:
        group.join(request.user, role="member")
        return redirect("group_members", slug=group.slug)


@require_POST
def group_invite(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    if not group.can_invite(request.user):
        raise Http404()
    
    form = GroupInviteForm(request.POST)
    
    if form.is_valid():
        for user in form.cleaned_data["user_identifiers"]:
            group.invite(user, request.user, role=form.cleaned_data["role"])
    
    return redirect("group_members", slug=group.slug)


@login_required
def group_invite_response(request, token):
    invite = get_object_or_404(GroupInvitation, token=token)
    ctx = {"invite": invite}
    
    if request.user != invite.user:
        redirect("group_detail", slug=invite.group.slug)
    
    if request.method == "POST":
        if "accept" in request.POST:
            invite.accept(request.user)
            if invite.group.access != "private":
                action.send(request.user, verb="joined", target=invite.group)
        
        if "decline" in request.POST:
            invite.decline()
        
        return redirect("group_detail", slug=invite.group.slug)
    else:
        ctx = RequestContext(request, ctx)
        return render_to_response("groups/group_invite_response.html", ctx)


@login_required
def group_add_layers(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    ctx = {}
    if request.method == "POST":
        form = GroupLayerForm(request.POST)
        
        if form.is_valid():
            ctx["layers_added"] = []
            for l in form.cleaned_data["layers"]:
                GroupLayer.objects.get_or_create(layer=l, group=group)
                if group.access != "private":
                    action.send(request.user, verb="added layer", action_object=l, target=group)
                ctx["layers_added"].append(l.title)
    else:
        form = GroupLayerForm()
    
    current_layers = GroupLayer.layers_for_group(group)
    
    form.fields["layers"].queryset = Layer.objects.filter(
            owner=request.user
            ).exclude(
            id__in=[li for li in current_layers.values_list('id', flat=True)]
    )
    
    
    ctx["form"] = form
    ctx.update({
        "object": group,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
        "current_layers": current_layers,
    })
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_add_layers.html", ctx)


@login_required
def group_add_maps(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    ctx = {}
    if request.method == "POST":
        form = GroupMapForm(request.POST)
        
        if form.is_valid():
            ctx["maps_added"] = []
            for m in form.cleaned_data["maps"]:
                GroupMap.objects.get_or_create(map=m, group=group)
                if group.access != "private":
                    action.send(request.user, verb="added map", action_object=m, target=group)
                ctx["maps_added"].append(m.title)
    else:
        form = GroupMapForm()
    
    current_maps = GroupMap.maps_for_group(group)
    
    form.fields["maps"].queryset = Map.objects.filter(
            owner=request.user
            ).exclude(
            id__in=[mi for mi in current_maps.values_list('id', flat=True)]
    )
    
    
    ctx["form"] = form
    ctx.update({
        "object": group,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
        "current_maps": current_maps,
    })
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_add_maps.html", ctx)


@login_required
def group_remove_maps_data(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if not group.user_is_role(request.user, "manager"):
        raise Http404()
    
    ctx = {}
    
    if request.method == "POST":
        map_form = GroupMapForm(request.POST)
        layer_form = GroupLayerForm(request.POST)
        
        if map_form.is_valid() and layer_form.is_valid():
            for m in map_form.cleaned_data["maps"]:
                GroupMap.objects.get(map=m).delete()
                if group.access != "private":
                    action.send(request.user, verb="removed map", action_object=m, target=group)
            map_form.cleaned_data["maps"] = []
            for l in layer_form.cleaned_data["layers"]:
                GroupLayer.objects.get(layer=l).delete()
                if group.access != "private":
                    action.send(request.user, verb="removed layer", action_object=l, target=group)
            layer_form.cleaned_data["layers"] = []
            
    # Even if we're removing data, recreate the forms so that they are missing the removed elements.
    map_ids = GroupMap.objects.filter(group=group).values_list("map", flat=True)
    layer_ids = GroupLayer.objects.filter(group=group).values_list("layer", flat=True)
    
    map_form = GroupMapForm()
    map_form.fields["maps"].queryset = Map.objects.filter(id__in=map_ids)
    
    layer_form = GroupLayerForm()
    layer_form.fields["layers"].queryset = Layer.objects.filter(id__in=layer_ids)
    
    ctx["map_form"] = map_form
    ctx["layer_form"] = layer_form
    
    ctx.update({
        "object": group,
        "members": group.member_queryset(),
        "is_member": group.user_is_member(request.user),
        "is_manager": group.user_is_role(request.user, "manager"),
    })
    
    ctx = RequestContext(request, ctx)
    return render_to_response("groups/group_remove_maps_data.html", ctx)
