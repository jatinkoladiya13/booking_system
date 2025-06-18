from django.shortcuts import render
from app.serializers import Userserializer, FitnessClassSerializer, BookingSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import Response
from rest_framework import status
from app.validators import is_strong_password, is_valid_email
from django.contrib.auth.models import User
from app.models import FitnessClass, Booking
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

# Create your views here.

@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password =   request.data.get('password')
        username =  request.data.get('username')

        if not is_valid_email(email):
            return Response({'status':'400', 'message': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        if not is_strong_password(password) :
            return Response({'status':'400','message': 'Password is not strong enough.'}, status=status.HTTP_400_BAD_REQUEST) 
         
        if User.objects.filter(username = username, email=email).exists():
            return Response({'status':'400','message': 'This username is already taken. Please choose another one.'}, status=status.HTTP_400_BAD_REQUEST) 

        serializer = Userserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200','message': 'User is successfully create ...!'}, status=status.HTTP_200_OK) 

    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)    


@csrf_exempt
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password') 
        
        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'status':'200','refresh': str(refresh), 'access': str(refresh.access_token),}, status=status.HTTP_200_OK) 
        else:
            return Response({'status':'400','message': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST) 
        
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
 
    if request.method == 'GET':
        user = request.user
        serializer = Userserializer(user)
        if serializer:
            return Response({'status':'200', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status':'400', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)      


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_fitness_class(request):
    if request.method == 'POST':
        name = request.data.get('name')
        datetime = request.data.get('datetime')
        instructor = request.data.get('instructor')
        available_slots = request.data.get('available_slots')

        if not all([datetime, instructor, available_slots]):
            return Response({'status': '400', 'message': 'All fields (datetime, instructor, available_slots) are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FitnessClass.objects.filter(datetime=datetime,instructor=instructor).exists():
            return Response({'status':'400','message': 'This username is already taken. Please choose another one.'}, status=status.HTTP_400_BAD_REQUEST) 

        serializer = FitnessClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': '200', 'message': 'Class created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status':'400', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_fitness_class(request):
    if request.method == 'GET':
        classes = FitnessClass.objects.filter(datetime__gte=timezone.now()).order_by('datetime')
        serializer = FitnessClassSerializer(classes, many=True)
        if serializer:
            return Response({'status':'200', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status':'400', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST) 

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def  book_class(request):
    if request.method == 'POST':
        class_id = request.data.get('class_id')

        if not class_id:
            return Response({'status': '400', 'message': 'class_id is required'}, status=status.HTTP_400_BAD_REQUEST)  

        try:
            fitness_class = FitnessClass.objects.get(id=class_id)
        except FitnessClass.DoesNotExist:
            return Response({'status':'400', 'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if Booking.objects.filter(user=request.user, fitness_class=fitness_class).exists():
            return Response({'status': '400', 'message': 'You have already booked this class'}, status=status.HTTP_400_BAD_REQUEST)
    

        if fitness_class.available_slots <= 0:
            return Response({'status':'400', 'message': 'No available slots'}, status=status.HTTP_404_NOT_FOUND)
        
        data = {
            'user': request.user.id,
            'fitness_class': fitness_class.id
        }

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            fitness_class.available_slots -= 1
            fitness_class.save() 
            return Response({'status':'200', 'message':'Booking successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':'400', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)         


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings(request):

    if request.method == 'GET':
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        
        if serializer:
            return Response({'status':'200', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status':'400', 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({'status':'400', 'message':'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)