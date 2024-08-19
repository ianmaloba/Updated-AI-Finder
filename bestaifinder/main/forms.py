from django import forms
from .models import AITool, Category
from ckeditor.widgets import CKEditorWidget

class TagWidget(forms.widgets.CheckboxSelectMultiple):
    template_name = 'widgets/tag_widget.html'
    
class AIToolForm(forms.ModelForm):
    ai_short_description = forms.CharField(widget=CKEditorWidget())
    ai_tags = forms.MultipleChoiceField(
        choices=[],
        widget=TagWidget,
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
        return ', '.join(ai_tags)
