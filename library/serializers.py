from rest_framework import serializers
from .models import *

class BookSerializer(serializers.ModelSerializer):

	class Meta:
		model = BookAdd
		fields = ('id', 'book_name', 'author', "entry_date", "description", "category" )



		