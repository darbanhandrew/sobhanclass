from inspect import Arguments
from graphene import relay, ObjectType, Field, Mutation
from graphene.types.scalars import ID, Boolean, String
from graphql_relay import from_global_id
from graphene_django_plus.types import ModelType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_plus.fields import CountableConnection
from .models import User, OTP
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


class OTPNode(ModelType):
    class Meta:
        model = OTP
        filter_fields = ['user']
        interfaces = (relay.Node,)
        connection_class = CountableConnection
        # When adding this to a query, only objects with a `can_read`
        # permission to the request's user will be allowed to return to him
        # Note that `can_read` was defined in the model.
        # If the model doesn't inherid from `GuardedModel`, `guardian` is not
        # installed or this list is empty, any object will be allowed.
        # This is empty by default

        # If unauthenticated users should be allowed to retrieve any object
        # of this type. This is not dependant on `GuardedModel` and neither
        # `guardian` and is defined as `False` by default
        public = True

        # A list of Django model permissions to check. Different from
        # object_permissions, this uses the basic Django's permission system
        # and thus is not dependant on `GuardedModel` and neither `guardian`.
        # This is an empty list by default.
        permissions = []


class UserQuery(ObjectType):
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)
    otp = relay.Node.Field(OTPNode)
    all_otps = DjangoFilterConnectionField(OTPNode)


# Mutations
# All Mutations related to users are defined here
class UserCreateMutation(ModelCreateMutation):
    class Meta:
        model = User

    @classmethod
    def before_save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input.get('password'))
        instance.is_active = False

    @classmethod
    def after_save(cls, info, instance, cleaned_input=None):
        # If the user created the object, allow him to modify it
        assign_perm('can_write', info.context.user, instance)
        assign_perm('can_read', info.context.user, instance)


class OTPVerifyMutation(Mutation):
    class Arguments:
        user_id = ID()
        otp_code = String()

    message = String()
    is_success = Boolean()

    @classmethod
    def mutate(cls, root, info, user_id, otp_code):
        user = User.objects.get(id=from_global_id(user_id)[1])
        otp = OTP.objects.get(user=user, otp=otp_code)
        if otp:
            otp.is_verified = True
            otp.save()
            return OTPVerifyMutation(message='OTP verified', is_success=True)
        else:
            return OTPVerifyMutation(message='OTP not verified', is_success=False)


class OTPSendMutation(Mutation):
    class Arguments:
        user_id = ID()

    message = String()
    is_success = Boolean()

    @classmethod
    def mutate(cls, root, info, user_id):
        user = User.objects.get(id=from_global_id(user_id)[1])
        otp = OTP.objects.create(user=user)
        if otp:
            return OTPSendMutation(message='OTP sent', is_success=True)
        else:
            return OTPSendMutation(message='OTP not sent', is_success=False)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = Field(UserNode)
    #profile = Field(ProfileNode)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class UserMutation(ObjectType):
    user_create = UserCreateMutation.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_otp = OTPVerifyMutation.Field()
    resend_otp = OTPSendMutation.Field()
