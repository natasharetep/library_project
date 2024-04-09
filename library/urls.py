from django.urls import path, include
from .views import *


from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path

from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()

router.register(r'/books', BookDetailViewSet, basename='book-detail')

urlpatterns = [
	path('viewset/', include(router.urls)),
	path('', home, name = 'home'),
	path('admin_login/', admin_login, name='admin_login'),
	path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
	path('book_add/', book_add, name='book_add'),
	path('logout_view/', logout_view, name='logout_view'),
	path('show_book/', show_book, name = 'show_book'),
	path('signup/', signup, name='signup'),
	path('student_login/', student_login, name='student_login'),
	path('student_dasboard/', student_dasboard, name='student_dasboard'),
	path('detail/<id>/', detail, name='detail'),
	path('requestbook/', requestbook, name='requestbook'),

	# path('admin/book-requests/', admin_book_requests, name='admin_book_requests'),
    # path('admin/handle-request/<int:book_id>/<str:action>/', handle_request, name='handle_request'),
   
    path('admin_book_requests/', admin_book_requests, name='admin_book_requests'),
    path('respond_to_request/<int:request_id>/<str:response>/', respond_to_request, name='respond_to_request'),
	path('notification/', notification, name='notification'),
   
	# path('profile/', profile, name='profile'),
	path('bookissue/', bookissue, name='bookissue'),
	# path('request_book/', request_book, name='request_book'),
	# path('book_detail/', book_detail, name='book_detail'),
	path('return_book/', return_book, name='return_book'),
	path('student_info/', student_info, name='student_info'),
	# path('return_request/', return_request, name='return_request'),
	path('return_book/', return_book, name='return_book'),
	# path('returned_book_events/', returned_book_events, name='returned_book_events'),


# api urls

	path('book/<id>/', book_detail_api),
	path('books/', book_list, name='book_list'),

	path('book-api/', BookList.as_view(), name='book-api'),
	path('book-api/<id>/', BookDetail.as_view()),

	path('book-list/', BookListGenericView.as_view()),
	path('books-detail/<id>/', BookDetailGenericView.as_view()),

	# path('book-search/', BookSearch.as_view()),

	path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),

# show data from api
	path('show_api/', show_api, name='show_api'),
]