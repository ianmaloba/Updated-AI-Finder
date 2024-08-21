from django import forms
from .models import AITool, Category
from ckeditor.widgets import CKEditorWidget

class TagWidget(forms.widgets.CheckboxSelectMultiple):
    template_name = 'widgets/tag_widget.html'
    
class AIToolForm(forms.ModelForm):
    ai_short_description = forms.CharField(widget=CKEditorWidget())
    ai_tags = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox',
            'style': 'display: inline-block; width: auto; margin-right: 10px;'
        }),
        required=False
    )
    ai_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'example: Sendbird AI Chatbot',
            'class': 'form-control'
        }),
        label="Enter the AI Tool Name"
    )
    ai_tool_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'example: https://aifinderguru.com/',
            'class': 'form-control'
        }),
        label="AI Tool Link"
    )
    ai_short_description = forms.CharField(
        widget=CKEditorWidget(attrs={
            'placeholder': 'example: Provide a description of your AI Tool',
            'class': 'form-control'
        }),
        label="AI Tool Description"
    )
    ai_pricing_tag = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'example: Free or $24/Month or Freemium ...',
            'class': 'form-control'
        }),
        label="Enter the AI Pricing Tag"
    )
    ai_tool_logo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }),
        label="AI Tool Logo",
        required=False
    )
    ai_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }),
        label="AI Tool Image",
        required=False
    )

    class Meta:
        model = AITool
        fields = ['ai_name', 'ai_image', 'ai_tool_logo', 'ai_short_description', 'ai_tool_link', 'ai_pricing_tag', 'ai_tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ai_image'].required = False
        self.fields['ai_tool_logo'].required = False
        self.fields['ai_pricing_tag'].required = False
        self.fields['ai_pricing_tag'].widget.attrs['maxlength'] = 25
        
        # Dynamically set choices for ai_tags
        all_tags = AITool.objects.values_list('ai_tags', flat=True).distinct()
        unique_tags = set(tag.strip() for tags in all_tags for tag in tags.split(',') if tag.strip() and tag.strip() != "#")
        self.fields['ai_tags'].choices = [(tag, tag) for tag in unique_tags]

    def clean_ai_pricing_tag(self):
        ai_pricing_tag = self.cleaned_data.get('ai_pricing_tag')
        if not ai_pricing_tag:
            return 'Pricing not specified'
        return ai_pricing_tag

    def clean_ai_tags(self):
        ai_tags = self.cleaned_data.get('ai_tags')
        if not ai_tags:
            raise forms.ValidationError("PLEASE SELECT ATLEAST ONE TAG.")
        return ', '.join(ai_tags)

from .models import ToolComment, ToolRating

class ToolCommentForm(forms.ModelForm):
    class Meta:
        model = ToolComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your comment...'}),
        }

class ToolRatingForm(forms.ModelForm):
    class Meta:
        model = ToolRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '5', 'step': '1'}),
        }