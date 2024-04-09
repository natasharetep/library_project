from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone

timezone.now()


class LoginModel(models.Model):
	username = models.CharField(max_length=200)
	password = models.CharField(max_length=100)

	def __str__(self):
		return self.username



BOOK_CATEGORY = [
    ('F','Fiction'),
    ('NF','Non-Fiction'),
    ('REF','Reference'),
    ('EDU','Educational'),
    ('M','Music'),
    ('A','Art')
]

class BookAdd(models.Model):
    book_name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    entry_date = models.DateField()
    category = models.CharField(choices=BOOK_CATEGORY, max_length=4)
    book_image = models.ImageField(upload_to = 'books')
    description = models.TextField()

    def __str__(self):
        return self.book_name


class BookRequest(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    book = models.ForeignKey(BookAdd, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_accepted = models.BooleanField(default=False)
    messages = models.CharField(max_length=200)
    


def expiry():
    return date.today() + timedelta(days=14)
    
class BookIssue(models.Model):
    bookname = models.ForeignKey(BookAdd, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(default=date.today)
    return_date = models.DateField(default=expiry)  # Adjust the default value

    def __str__(self):
        return str(self.bookname)  # Convert the bookname to a string representation

class ReturnBook(models.Model):
    rtbook = models.ForeignKey(BookAdd, on_delete=models.CASCADE, null=True, blank=True)
    stu = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    rtn_date = models.DateField(default=date.today)  

    def __str__(self):
        return str(self.rtbook)


class Notification(models.Model):
    name = models.ForeignKey(BookAdd, on_delete=models.CASCADE)
    student_name = models.ForeignKey(User, on_delete=models.CASCADE)
    messages = models.TextField()  # Change to TextField for potentially longer messages

    def __str__(self):
        return f"{self.student_name.username} - {self.messages}"

    def display_message(self):
        return f"{self.student_name.username} - {self.messages}"