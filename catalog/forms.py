from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime #for checking renewal date range.

# Para la página que permita a los bibilotecarios renovar los libros prestados introduciendo una fecha de renovación (renewal_date) usaremos un formulario
# crearemos un formulario con la clase Form que permita a los usuarios introducir una fecha. Rellenaremos el campo con un valor inicial de 3 semanas desde la fecha actual 
# (el periodo de préstamo normal), y añadiremos alguna validación para asegurar que el bibilotecario no pueda introducir una fecha pasada o una demasiado lejana en el futuro. 
# Cuando se haya introducido una fecha válida, la escribiremos sobre el campo BookInstance.due_back del registro actual.

class RenewBookForm(forms.Form):
    # el campo aceptará fechas utilizando los input_formats: AAAA-MM-DD (2016-11-06), MM / DD / AAAA (26/02/2016), MM / DD / AA ( 25/10/16), y se representará con el widget predeterminado: DateInput.
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        #Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data
    
        # obtenemos nuestros datos usando self.cleaned_data['renewal_date'] y devolvemos estos datos si los cambiamos o no al final de la función. 
        # Este paso nos permite "limpiar" y desinfectar los datos de entrada potencialmente insegura utilizando los validadores predeterminados,
        # y convertirlos al tipo estándar correcto para los datos (en este caso, un objeto Python datetime.datetime).
    

# el código anterior sirve para validar una solicitud de formulario para renovar un bookinstance, pero no estamos relacionandolo directamente con el módelo
# lo que hacemos es si se valida la fecha de renovación al ser envíada esta se guarda en la información del módelo en la vista. Claro que esto no es un problema porque es solo un campo, pero pueden ser varias líneas de código de ser más campos
# si solo necesita un formulario para asignar los campos de un solo modelo, entonces su modelo ya definirá la mayor parte de la información que necesita en su formulario: campos, etiquetas, texto de ayuda, etc.
# En lugar de recrear las definiciones de modelo en su formulario, es más fácil usar una clase auxiliar ModelForm para crear el formulario a partir de su modelo.

# todo lo que necesita hacer para crear el formulario es agregar class Meta with the associated model (BookInstance) y 
# una lista de los campos del modelo fields para incluir en el formulario (puede incluir todos los campos usando fields = '__all__', o puedes usar exclude (en vez de fields) para especificar los campos que no se incluirán del modelo).
    
# class RenewBookModelForm(ModelForm):
# class Meta:
    # model = BookInstance
    # fields = ['due_back',]

    # Si algunos campos no son del todo correctos, entonces podemos anularlos en nuestro class Meta, especificando un diccionario que contiene el campo a cambiar y su nuevo valor. 
    # Por ejemplo, en este formulario podríamos querer una etiqueta para nuestro campo de "Fecha de renovación" (en lugar del valor predeterminado basado en el nombre del campo: Fecha de vencimiento), 
    # y también queremos que nuestro texto de ayuda sea específico para este caso de uso.

    # labels = { 'due_back': _('Renewal date'), }
    # help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), }

    # Para agregar validación, puede usar el mismo enfoque que para un normal Form — define una función llamada clean_field_name() y coloca (raise) ValidationError excepciones para valores no válidos. 
    # La única diferencia con respecto a nuestro formulario original es que el campo modelo se llama due_back y no "renewal_date".