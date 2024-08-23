from django import forms
from .models import AITool
from ckeditor.widgets import CKEditorWidget
from django.utils.safestring import mark_safe

class InlineCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'widgets/inline_checkbox_select.html'

class AIToolForm(forms.ModelForm):
    ai_short_description = forms.CharField(widget=CKEditorWidget(config_name='default'))
    ai_tags = forms.MultipleChoiceField(
        choices=[],
        widget=InlineCheckboxSelectMultiple,
        help_text='Select a minimum of 1 and maximum of 10 related tags.',
        label="SELECT RELATED TAGS",
        required=False   
    )
    ai_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'example: ChatGPT',
            'class': 'form-control'
        }),
        label="ENTER THE AI TOOL NAME",
        help_text='Enter name of your AI tool.'
    )
    ai_tool_link = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'example: https://aifinderguru.com/',
            'class': 'form-control'
        }),
        label="AI TOOL LINK",
        help_text='Enter a valid URL for your AI tool.'
    )
    ai_short_description = forms.CharField(
        widget=CKEditorWidget(attrs={
            'placeholder': 'example: Provide a description of your AI Tool',
            'class': 'form-control'
        }),
        label="AI TOOL DESCRIPTION",
        help_text='Provide a brief description of your AI tool and its features and pricing. Appending YouTube vedio or Uploading/Drag and Drop any kind of files are allowed.'
    )
    ai_pricing_tag = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'example: Free or $24/Month or Freemium ...',
            'class': 'form-control'
        }),
        label="ENTER THE AI PRICING TAG",
        help_text='Specify the pricing model for your AI tool.'
    )
    ai_tool_logo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }),
        label="AI TOOL LOGO",
        help_text='Upload a logo for your AI tool. Allowed formats: PNG, JPG, GIF, JPEG.',
        required=False
    )
    ai_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }),
        label="AI TOOL GIF/IMAGE",
        help_text='Upload a gif or an image showcasing your AI tool, for example the website screenshot. Allowed formats: GIF, PNG, JPG, JPEG.',
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
        self.fields['ai_tags'].choices = [(tag, tag) for tag in sorted(unique_tags)]

        # If editing an existing tool, set initial values for ai_tags
        if self.instance.pk:
            self.fields['ai_tags'].initial = [tag.strip() for tag in self.instance.ai_tags.split(',')]

    def clean_ai_pricing_tag(self):
        ai_pricing_tag = self.cleaned_data.get('ai_pricing_tag')
        if not ai_pricing_tag:
            return 'Pricing not specified'
        return ai_pricing_tag

    def clean_ai_tags(self):
        ai_tags = self.cleaned_data.get('ai_tags')
        if not ai_tags:
            raise forms.ValidationError("Please select at least one tag.")
        if len(ai_tags) > 10:
            raise forms.ValidationError("Please select no more than 10 tags.")
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