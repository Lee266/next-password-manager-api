from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from app.models import User, Message, PasswordManage, Task, Calendar, PasswordGroup, PasswordTag, PasswordCustomField
from app.api.serializers import UserSerializer, MessageSerializer, PasswordManageSerializer, TaskSerializer, CalendarSerializer, PasswordCustomFieldSerializer, PasswordGroupSerializer, PasswordTagSerializer


class UserView(generics.ListCreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

class MessageView(generics.ListCreateAPIView):
  queryset = Message.objects.all()
  serializer_class = MessageSerializer
  permission_classes = (AllowAny,)
  
class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

class PasswordManageViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordManageSerializer
  queryset = PasswordManage.objects.all()
  model = PasswordManage
  # permission_classes = [IsAuthenticated]
  permission_classes = (AllowAny,)
  
  def create(self, request, *args, **kwargs):
    user_id = request.data.get('user')
    group_id = request.data.get('group')
    tag_id = request.data.get('tag')
    # custom_ids = request.data.get('custom')

    # Check user_id that is required
    if not user_id:
        return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response({'error': f'User ID {user_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    # Check group and tag. These are able to null
    group = None
    tag = None
    if group_id:
        try: group = PasswordGroup.objects.get(id=group_id)
        except ObjectDoesNotExist:
            return Response({'error': f'Group ID {group_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    if tag_id:
        try: tag = PasswordTag.objects.get(id=tag_id)
        except ObjectDoesNotExist:
            return Response({'error': f'Tag ID {tag_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Compute the index based on the last 'PasswordManage' record for the given group
    if group:
        last_password_manage = PasswordManage.objects.filter(group=group).order_by('-index').first()
    else:
        last_password_manage = PasswordManage.objects.filter(group__isnull=True).order_by('-index').first()
    # Index set 0 if not record in database
    next_index = last_password_manage.index + 1 if last_password_manage else 0
    
    data = {k: v for k, v in request.data.items() if k not in ['user', 'group', 'tag']}
    # Save to database 
    password_manage = PasswordManage.objects.create(user=user, group=group, tag=tag, index=next_index, **data)
    # password_manage.save()
    serializer = self.get_serializer(password_manage)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['get'])
  def columns(self):
    serializer = self.get_serializer()
    columns = [field for field in serializer.fields.keys()]
    return Response(columns)
  
  @action(detail=False, methods=['post'])
  def search(self, request):
    userID = request.data["id"]
    queryset = self.get_queryset().filter(user_id=userID)
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.model.objects.filter(user_id=userID).select_related('group', 'tag').prefetch_related('custom').order_by('index')
    serializer = self.get_serializer(queryset, many=True)
    # Get a list of all unique group names from the Group model
    group_names = PasswordGroup.objects.filter(user_id=userID).values_list('group_name', flat=True).distinct()
    grouped_data = {group_name: [] for group_name in group_names}
    grouped_data['group'] = []

    for data in serializer.data:
        groupData = data['group']
        if groupData is None:
            group_key = 'group'
        else:
            group_key = groupData["group_name"]
        
        if group_key in grouped_data:
            grouped_data[group_key].append(data)
        else:
            grouped_data[group_key] = [data]

    return Response(grouped_data)
  
  @action(detail=False, methods=['patch'])
  def update_indexes(self, request):
    print("move update_indexes")
    passwords_data = request.data.get('new_passwords')
    old_passwords_data = request.data.get('old_passwords', [])
    old_group_id = request.data.get('old_group_id')
    new_group_id = request.data.get('new_group_id')
    old_group = get_object_or_404(PasswordGroup, pk=old_group_id)
    new_group = get_object_or_404(PasswordGroup, pk=new_group_id)
    print("old_group")
    print(old_group)
    print("new_group")
    print(new_group)
    if passwords_data is not None:
    # Temporarily set indices to None to avoid uniqueness constraint violation
      for password_data in passwords_data + old_passwords_data:
          password_id = password_data.get('id')
          if password_id is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.index = None
              password.save()

      # Set the new indices
      for password_data in passwords_data:
          password_id = password_data.get('id') 
          new_index = password_data.get('index')
          if password_id is not None and new_index is not None and new_group_id is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.group = new_group
              password.index = new_index
              password.save()
      if (old_passwords_data):
        for password_data in passwords_data:
          password_id = password_data.get('id') 
          new_index = password_data.get('index')
          if password_id is not None and new_index is not None and new_group_id is not None:
              password = PasswordManage.objects.get(pk=password_id)
              password.group = old_group
              password.index = new_index
              password.save()

      return Response({"detail": "Password indices updated."}, status=status.HTTP_200_OK)
    else:
      return Response({"detail": "Passwords not provided."}, status=status.HTTP_400_BAD_REQUEST)
  

class PasswordGroupViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordGroupSerializer
  queryset = PasswordGroup.objects.all()
  # permission_classes = [IsAuthenticated]
  permission_classes = (AllowAny,)
  model = PasswordGroup
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.get_queryset().filter(user_id=userID).values('id', 'group_name')
    return Response(list(queryset))

class PasswordTagViewSet(viewsets.ModelViewSet):
  serializer_class = PasswordTagSerializer
  queryset = PasswordTag.objects.all()
  permission_classes = (AllowAny,)
  model = PasswordTag
  
  @action(detail=False, methods=['post'])
  def get_data(self, request):
    userID = request.data["user_id"]
    queryset = self.get_queryset().filter(user_id=userID).values('id', 'tag_name')
    return Response(list(queryset))

class PasswordManageView(generics.ListCreateAPIView):
  queryset = PasswordManage.objects.all()
  serializer_class = PasswordManageSerializer
  permission_classes = (AllowAny,)

class TaskViewSet(viewsets.ModelViewSet):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  permission_classes = (AllowAny,)

class CalendarViewSet(viewsets.ModelViewSet):
  queryset = Calendar.objects.all()
  serializer_class = CalendarSerializer
  permission_classes = (AllowAny,)


@api_view(['GET', 'POST'])
def task_list(request):
  if request.method == 'GET':
        Tasks = Task.objects.all()
        serializer = TaskSerializer(Tasks, many=True)
        return JsonResponse(serializer.data)
  elif request.method == 'POST':
      serializer = TaskSerializer(data=request.data)
      if serializer.is_valid():
          serializer.save()
          return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestAppView(APIView):
  permission_classes = (AllowAny,)
  def get(self, request, **kwargs):
    return JsonResponse({ "data": "this is get" })
  def post(self, request, **kwargs):
    return JsonResponse({ "data": "post" })
  def put(self, request, **kwargs):
    return JsonResponse({ "data": "put" })
  def patch(self, request, **kwargs):
    return JsonResponse({ "data": "patch" })
  def delete(self, request, **kwargs):
    return JsonResponse({ "data": "delete" })

  