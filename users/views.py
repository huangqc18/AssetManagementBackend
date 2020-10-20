''' user/view.py, all in domain api/user/ '''
import jwt
from django.core.exceptions import ValidationError

from app.settings import SECRET_KEY
from app.utils import gen_response, parse_args
from .models import User


def auth_permission_required(*perms):
    ''' 
    用于用户验证的装饰器
    该装饰器会验证 cookies 里的 token 是否合法，
    并将对应用户以参数 user 传给被装饰函数
    错误时返回 status=1, code=401
    例:
    @auth_permission_required(users.IT, users.SYSTEM)
    def foo():
        pass
    '''
    def decorator(view_func):
        ''' 多嵌套一层，为了给装饰器传参 '''
        def _wrapped_view(request, *args, **kwargs):
            ''' 装饰器内函数 '''
            try:
                token = request.COOKIES['Token']
            except KeyError:
                return gen_response(status=1, code=401, message='Token 未给出')
            try:
                decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                username = decoded['username']
            except jwt.ExpiredSignatureError:
                return gen_response(status=1, message='Token 已过期', code=401)
            except jwt.InvalidTokenError:
                return gen_response(status=1, message='Token 不合法', code=401)

            try:
                user: User = User.objects.get(username=username)
            except User.DoesNotExist:
                return gen_response(status=1, message='用户不存在', code=401)

            if user.token != token:
                return gen_response(status=1, message='用户不在线', code=401)
            if not user.is_active:
                return gen_response(status=1, message='用户未激活', code=401)
            if not user.has_perms(perms):
                return gen_response(status=1, message='用户权限不足', code=401)

            return view_func(request, user=user, *args, **kwargs)
        return _wrapped_view
    return decorator


# @auth_permission_required('users.SYSTEM')
def user_list(request):
    ''' api/user/list GET
    返回所有用户的列表。
    return: data([{}]), code =
        200: success
    '''
    if request.method == 'GET':
        all_users = User.objects.filter()
        res = [{
            'name': user.username,
            'department': user.department,
            'role': user.gen_roles(),
            'is_active': user.is_active,
        } for user in all_users]

        return gen_response(code=200, data=res, message='获取用户列表')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


# @auth_permission_required('users.SYSTEM')
def user_delete(request):
    ''' api/user/delete POST
    删除用户。
    para: name(str)
    return: code =
        200: success
        201: parameter error
        202: no such named user
        203: admin can't be deleted
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]

        if name == 'admin':
            return gen_response(message='admin 不能被删除', code=203)
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            return gen_response(message='用户不存在', code=202)
        user.delete()
        return gen_response(code=200, message=f'删除用户 {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def user_exist(request):
    ''' api/user/exist POST
    用户名是否存在。
    para: name(str)
    return: exist(bool), code =
        200: success
        201: parameter error
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name')
        if not valid:
            return gen_response(code=201, message=res)
        name = res[0]
        exist = True
        try:
            User.objects.get(username=name)
        except User.DoesNotExist:
            exist = False
        return gen_response(code=200, exist=exist)
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


# @auth_permission_required('users.SYSTEM')
def user_add(request):
    '''  api/user/add POST
    添加用户。
    para: name(str), password(str), department(str), role([...])
    return: code =
        200: success
        201: parameter error
        400: Validation Error when saving user
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name', 'password', 'department', 'role')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd, department, roles = res

        user = User(username=name,
                    department=department)
        user.set_password(pwd)

        try:
            user.full_clean()
            user.save()
        except ValidationError as error:
            return gen_response(message=str(error), code=400)
        user.set_roles(roles)
        return gen_response(code=200, message=f'添加用户 {name}')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


# @auth_permission_required('users.SYSTEM')
def user_edit(request):
    '''  api/user/edit POST
    编辑用户。
    para: name(str), password(str), department(str), role([...])
    return: code =
        200: success
        201: parameter error
        202：no such user
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'name', 'password', 'department', 'role')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd, department, roles = res
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            return gen_response(message='用户不存在', code=202)
        user.set_password(pwd)
        user.department = department
        user.save()
        user.set_roles(roles)

        return gen_response(code=200, message=f'{user.username} 信息修改')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


# @auth_permission_required('users.SYSTEM')
def user_lock(request):
    ''' api/user/lock POST
    锁定用户
    para: username(str), active(0/1)
    return: code =
        200: success
        201: parameter error
        202：no such user
        203: admin can not be locked
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'username', 'active')
        if not valid:
            return gen_response(code=201, message=res)
        username, active = res
        if username == 'admin':
            return gen_response(message='admin 必须处于活跃状态', code=203)
        user = User.objects.filter(username=username)
        if not user:
            return gen_response(message='用户不存在', code=202)

        user.update(is_active=active)
        return gen_response(code=200)
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


def user_login(request):
    '''  api/user/login POST
    用户登录。
    para: name(str), password(str)
    return: code =
        201: parameter error
        status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        valid, res = parse_args(request.body, 'username', 'password')
        if not valid:
            return gen_response(code=201, message=res)
        name, pwd = res
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            return gen_response(message='用户不存在', status=1)

        if not user.check_password(pwd):
            return gen_response(message='密码有误', status=1)
        if not user.is_active:
            return gen_response(message='用户不处于活跃状态', status=1)

        user.token = user.generate_jwt_token()
        user.save()

        return gen_response(token=user.token, status=0, message=f'{name} 登录')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


@auth_permission_required()
def user_logout(request, user):
    '''  api/user/login POST
    用户登出。
    return: status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        user.token = ''
        user.save()

        return gen_response(status=0, message=f'{user.username} 登出')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')


@auth_permission_required()
def user_info(request, user):
    '''  api/user/login POST
    用户信息。
    return: userInfo = {name(str), role([]), avatar('')}
        status =
        0: success
        1: fall
    '''
    if request.method == 'POST':
        info = {
            "name": user.username,
            "role": user.gen_roles(),
            "avatar": ''
        }
        return gen_response(status=0, userInfo=info, message=f'{user.username} 获取用户信息')
    return gen_response(code=405, message=f'Http 方法 {request.method} 是不被允许的')
