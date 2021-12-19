from graphene import relay, ObjectType
from graphene_django_plus.types import ModelType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_plus.fields import CountableConnection
from .models import User
from guardian.shortcuts import assign_perm, remove_perm
from graphene_django_plus.mutations import (
    ModelCreateMutation,
)
import graphql_jwt


class UserNode(ModelType):
    class Meta:
        model = User
        filter_fields = ['username', 'email']
        interfaces = (relay.Node,)
        connection_class = CountableConnection
        # When adding this to a query, only objects with a `can_read`
        # permission to the request's user will be allowed to return to him
        # Note that `can_read` was defined in the model.
        # If the model doesn't inherid from `GuardedModel`, `guardian` is not
        # installed or this list is empty, any object will be allowed.
        # This is empty by default
        object_permissions = ['can_read', 'can_write']

        # If unauthenticated users should be allowed to retrieve any object
        # of this type. This is not dependant on `GuardedModel` and neither
        # `guardian` and is defined as `False` by default
        public = False

        # A list of Django model permissions to check. Different from
        # object_permissions, this uses the basic Django's permission system
        # and thus is not dependant on `GuardedModel` and neither `guardian`.
        # This is an empty list by default.
        permissions = []


class UserQuery(ObjectType):
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)


# Mutations
# All Mutations related to users are defined here
class UserCreateMutation(ModelCreateMutation):
    class Meta:
        model = User

    @classmethod
    def before_save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input.get('password'))

    @classmethod
    def after_save(cls, info, instance, cleaned_input=None):
        # If the user created the object, allow him to modify it
        assign_perm('can_write', info.context.user, instance)
        assign_perm('can_read', info.context.user, instance)


class UserMutation(ObjectType):
    user_create = UserCreateMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
