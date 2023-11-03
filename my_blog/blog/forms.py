from django import forms
from .models import Post, Comment, Tag, Category

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'thumb_image', 'file_upload', 'category', 'new_category']

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="(Select a category)",
        required=False,
    )
    new_category = forms.CharField(max_length=50, required=False)

    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        empty_label="(Select a tag)",
        required=False,
    )
    new_tag = forms.CharField(max_length=50, required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']