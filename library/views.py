from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view


def home(request):
	return render(request, 'home.html', {'home':home})


@csrf_protect
def admin_login(request):


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            print(user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials for admin login.')

    return render(request, 'registration/login_admin.html')


def admin_dashboard(request):
    return render(request, 'adminfolder/admin_dashboard.html')


def book_add(request):
    if request.method == "POST":
        form = BookAddForm(request.POST, request.FILES)

        # Set required attribute to False for book_image if it's not in FILES
        if 'book_image' not in request.FILES:
            form.fields['book_image'].required = False

        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_add')  # Redirect to the book list page or another appropriate page
        else:
            print(form.errors)
            messages.error(request, 'Form submission failed. Please correct the errors.')
            return render(request, 'adminfolder/book_add.html', {'form': form})

    else:
        # If it's a GET request, create a new form instance
        form = BookAddForm()

    return render(request, 'adminfolder/book_add.html', {'form': form})

def show_book(request):
	book_list =BookAdd.objects.all()
	context = {'book_list': book_list}
	return render(request, 'adminfolder/books_detail.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('home')


# student  section

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('student_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def student_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                auth_login(request, user)

                return redirect('student_dasboard')
            else:
                
                return redirect('signup')

        # Handle form errors if needed.
        # pass

        form = AuthenticationForm() 
    return render(request, 'registration/login_student.html')

def student_dasboard(request):
    book_category = request.GET.get('category', None)
    
    if book_category:
        book_list = BookAdd.objects.filter(category=book_category)
    else:
        book_list = BookAdd.objects.all()

    context = {'book_list': book_list, 'book_category': book_category, 'book_categories': BOOK_CATEGORY}
    return render(request, 'studentfolder/student_dasboard.html', context)


def detail(request, id):
 
    detail =BookAdd.objects.get(id=id)
    bookissue = BookAdd.objects.filter(book_name=detail)
    book_issued = BookIssue.objects.filter(bookname=detail).exists()
    context = {'detail': detail, 'book_issued':book_issued}
    return render(request, 'studentfolder/detail.html', context)


def requestbook(request):
    if request.method == 'GET' and request.GET.get('ajax_request'):
        book_id = request.GET.get('book_id')
        bookcode = get_object_or_404(BookAdd, id=book_id)
        user = request.user  # Assuming the user is authenticated
        
        # Create BookRequest instance
        book_request = BookRequest.objects.create(book=bookcode, user=user, status=BookRequest.PENDING)
        # messages = Notification.objects.create(
        #         name=bookcode.book_name,  # Provide a valid value for the name field
        #         student_name=bookcode.user,
        #         messages=f'Request for book sent.'

        #     )
        print('this book is ', bookcode)
        
        data = {'message': f'Book {book_id} requested successfully!', 'status': 'pending'}
        # messages = Notification.objects.create(messages=data)
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'})



def admin_book_requests(request):
    book_requests = BookRequest.objects.filter(status=BookRequest.PENDING)
    book_ids_with_requests = list(book_requests.values_list('book_id', flat=True))
    print("Book IDs with Requests:", book_ids_with_requests)

    return render(request, 'admin_book_requests.html', {
        'book_requests': book_requests,
        'book_ids_with_requests': book_ids_with_requests,
    })

def notification(request):
    messages = Notification.objects.all()
    return render(request, 'notification.html', {'messages': messages})

def respond_to_request(request, request_id, response):
    book_request = get_object_or_404(BookRequest, id=request_id)

    if response == 'accept':
        # Check if the book has already been issued
        if BookIssue.objects.filter(bookname=book_request.book, student=book_request.user).exists():
            return JsonResponse({'error': 'Book already issued to this user'})

        # Check if the book is pending or rejected
        if book_request.status == BookRequest.PENDING:
            book_request.status = BookRequest.ACCEPTED
            book_request.admin_accepted = True
            book_request.save()

            # Create a BookIssue instance
            book_issue = BookIssue.objects.create(
                bookname=book_request.book,
                student=book_request.user,
                issue_date=timezone.now().date(),
                return_date=expiry(),
            )
            messages = Notification.objects.create(
                name=book_request.book,  # Provide a valid value for the name field
                student_name=book_request.user,
                messages=f'Request for book "{book_request.book.book_name}" accepted.'

            )

            # return HttpResponseRedirect('notification')

            # messages.success(request, f'Request for book "{book_request.book.book_name}" accepted.')
           
            return JsonResponse({'message': 'Request accepted', 'status': 'accepted'})

        elif book_request.status == BookRequest.REJECTED:
            return JsonResponse({'error': 'Book request was rejected'})
        else:
            return JsonResponse({'error': 'Book already issued to this user'})
    elif response == 'reject':
        book_request.status = BookRequest.REJECTED
        book_request.save()

        messages.success(request, f'Request for book "{book_request.book.book_name}" rejected.')
        
        return JsonResponse({'message': 'Request rejected', 'status': 'rejected'})
    else:
        return JsonResponse({'error': 'Invalid response'})



def bookissue(request):
    bookissue = BookIssue.objects.filter(student=request.user)
    returned_books = ReturnBook.objects.filter(stu=request.user)

    returned_book_ids = set(returned_book.rtbook.id for returned_book in returned_books)

    for book in bookissue:
        book.returned = book.id in returned_book_ids

    context = {'bookissue': bookissue}
    return render(request, 'studentfolder/profile.html', context)


# def return_book(request):
#     if request.method == 'GET':
#         return_book_id = request.GET.get('return_book_id')
#         book_issue = get_object_or_404(BookIssue, id=return_book_id)
#         user = request.user 
#         return_book = ReturnBook.objects.create(rtbook=book_issue.bookname, stu=user, borrow_date=book_issue.issue_date)

#         book_issue.return_date = timezone.now().date()
#         book_issue.save()

#         return JsonResponse({'message': 'Returned Book', 'return_date': book_issue.return_date})
#     else:
        # return JsonResponse({'message': 'Error in book returned'})

# from django.core.mail import send_mail

def return_book(request):
    if request.method == 'GET':
        return_book_id = request.GET.get('return_book_id')
        book_issue = get_object_or_404(BookIssue, id=return_book_id)

        # Uncomment the following lines if you want to check the due date
        # if book_issue.due_date >= timezone.now().date():
        #     return JsonResponse({'message': 'Book returned after the due date'})

        user = request.user 

        # Create ReturnBook record
        return_book = ReturnBook.objects.create(rtbook=book_issue.bookname, stu=user, borrow_date=book_issue.issue_date, rtn_date=timezone.now().date())

        # Update BookIssue record
        book_issue.return_date = timezone.now().date()
        book_issue.save()

        book_issue.delete()

        # Send a message to the admin (commented out for now)
        admin_message = f"User {user.username} returned book {book_issue.bookname} on {timezone.now().date()}."
        # send_mail('Book Returned', admin_message, 'from@example.com', ['admin@example.com'])

        return JsonResponse({'message': 'Returned Book', 'return_date': book_issue.return_date})
    else:
        return JsonResponse({'message': 'Error in book returned'})


def student_info(request):
    record = BookIssue.objects.all()
    context = {'record':record}
    return render(request, 'adminfolder/student_info.html', context)


#pract


# def book_detail(request):
#     issued_book = BookIssue.objects.filter(student=request.user)
#     context = {'issued_book':issued_book}
#     return render(request, 'studentfolder/book_detail.html', context)



       







# API----

from .serializers import BookSerializer
import datetime
import requests

def show_api(request):
    response = requests.get('http://127.0.0.1:8000/books/')
    list_data = response.json()
    return render(request, 'studentfolder/student_dasboard.html', {'list_data':list_data})

@api_view(['GET', 'POST'])
def book_list(request):

    if request.method == 'GET' and request.GET.get('ajax_request'):
        books = BookAdd.objects.all()
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)


    if request.method == 'POST':
        data = request.data
        data['entry_date'] = datetime.date.today()

        serializer = BookSerializer(data=data)
        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT','PATCH', 'DELETE'])

def book_detail_api(request, id):

    try:
        book = BookAdd.objects.get(id=id)
    except BookAdd.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method =="GET":
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method=="PUT":
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():   
            serializer.save()
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework.views import APIView
from django.http import Http404


class BookList(APIView):
    """
    List all books, or create a new book.
    """
    def get(self, request):
        books = BookAdd.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class BookDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """ 
    permission_classes = [AllowAny]


    def get_object(self, id):
        try:
            return BookAdd.objects.get(id=id)
        except BookAdd.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        books = self.get_object(id)
        serializer = BookSerializer(books)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        books = self.get_object(id)
        print(books)
        serializer = BookSerializer(books, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, id, format=None):
        books = self.get_object(id)
        serializer = BookSerializer(books, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id, format=None):
        books = self.get_object(id)
        books.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





from rest_framework import mixins, generics, viewsets
from rest_framework import filters

# class BookSearch(generics.ListAPIView):
#     queryset = BookAdd.objects.all()
#     serializer_class = BookSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['book_name']

class BookListGenericView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    queryset = BookAdd.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['book_name']

    def get(self, request, *args, **kwargs):


        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
from rest_framework.permissions import IsAuthenticated



class BookDetailGenericView(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    lookup_field = 'id'
    queryset = BookAdd.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        
        return self.destroy(request, *args, **kwargs)


from rest_framework import permissions

# class BookViewSet(viewsets.ModelViewSet):
#     serializer_class = BookSerializer
#     queryset = BookAdd.objects.all()
#     permission_classes = [permissions.AllowAny]





class BookDetailViewSet(viewsets.ViewSet):
    lookup_field = 'id'

    def list(self, request):
        books = BookAdd.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, id):
        book = self.get_object(id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def update(self, request, id):
        book = self.get_object(id)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id):
        book = self.get_object(id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def get_object(self, id):
        try:
            return BookAdd.objects.get(id=id)
        except BookAdd.DoesNotExist:
            raise NotFound("Book not found")
        

