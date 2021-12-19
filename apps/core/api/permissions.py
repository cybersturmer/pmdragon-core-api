from rest_framework import permissions

from apps.core.models import Person


class IsOwnerOrReadOnly(permissions.BasePermission):
	"""
	Allow update / remove to object only if current user
	is determined as an owner in created_by field.
	For others this permission allow only read access.
	We use it for example in IssueMessages.
	"""
	def has_object_permission(self, request, view, obj) -> bool:
		if request.method in permissions.SAFE_METHODS:
			return True

		if not hasattr(obj, 'owned_by'):
			return False

		try:
			return obj.owned_by == request.user.person
		except Person.DoesNotExist:
			return False


class IsCreatorOrReadOnly(permissions.BasePermission):
	"""
	For this to work we need to be auth.
	Model should contain created by field.
	Just because maybe we dont have user data in
	"""
	def has_object_permission(self, request, view, obj) -> bool:
		if request.method in permissions.SAFE_METHODS:
			return True

		if not hasattr(obj, 'created_by'):
			return False

		try:
			return obj.created_by == request.user.person
		except Person.DoesNotExist:
			return False


class IsParticipateInWorkspace(permissions.BasePermission):
	"""
	Allow access to object if object workspace do not determined
	Or current user participate in workspace
	"""
	def has_object_permission(self, request, view, obj) -> bool:
		try:
			if request.user.person in obj.workspace.participants.all():
				return True
		except Person.DoesNotExist:
			return False

		return False


class WorkspaceOwnerOrReadOnly(permissions.BasePermission):
	"""
	Allow access to everyone, but allow changing only for owner.
	We use it to prevent workspace or project changes by non-owner.
	"""
	def has_object_permission(self, request, view, obj) -> bool:
		if request.method in permissions.SAFE_METHODS:
			return True

		if not hasattr(obj, 'workspace'):
			return False

		try:
			if request.user.person == obj.workspace.owned_by:
				return True
		except Person.DoesNotExist:
			return False

		return False


class IsMeOrReadOnly(permissions.BasePermission):
	"""
	Allow access to Person if its me.
	Reject update / delete for others
	We will use it in all Person related views.
	"""
	def has_object_permission(self, request, view, obj: Person) -> bool:
		if request.method in permissions.SAFE_METHODS:
			return True

		try:
			return request.user.person == obj
		except Person.DoesNotExist:
			return False
