from django import forms
from .models import Employee, Department


class EmployeeForm(forms.ModelForm):
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date d'embauche"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Date de fin"
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 'photo',
            'employee_id', 'department', 'position', 'contract_type',
            'status', 'hire_date', 'end_date', 'salary'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Masquer le salaire pour les non-RH/ADMIN
        if user and not user.can_edit_employees:
            self.fields.pop('salary', None)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Employee.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre employé.")
        return email

    def clean_employee_id(self):
        emp_id = self.cleaned_data.get('employee_id')
        qs = Employee.objects.filter(employee_id=emp_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce matricule est déjà utilisé.")
        return emp_id


class EmployeeFilterForm(forms.Form):
    search = forms.CharField(required=False, label="Rechercher",
                             widget=forms.TextInput(attrs={'placeholder': 'Nom, email, matricule...'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False,
                                        empty_label="Tous les départements")
    status = forms.ChoiceField(choices=[('', 'Tous les statuts')] + Employee.STATUS_CHOICES, required=False)
    contract_type = forms.ChoiceField(choices=[('', 'Tous les contrats')] + Employee.CONTRACT_CHOICES, required=False)
