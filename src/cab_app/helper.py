"""Helper functions for cab_app"""

def auth_login(user_id):
    obj = UserAccount.objects.update_or_create(user_id=user_id, defaults={'login_at':timezone.now(),
        'session_active':True, 'email_verified':True})


def auth_logout(user_id):
    objs = UserAccount.objects.filter(user_id=user_id)
    if objs:
        obj = objs[0]
        last_login = obj.login_at
        obj = UserAccount.objects.filter(user_id=user_id).update(last_logout=timezone.now(), session_active=False, last_login=last_login)
    else:
        UserAccount.objects.filter(user_id=user_id).update(last_logout=timezone.now(), session_active=False)
    
