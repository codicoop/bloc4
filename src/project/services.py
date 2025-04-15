def user_have_entity_and_verified_email(user):
    return user.email_verified and user.entity
