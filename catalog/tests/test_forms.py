from django.test import TestCase

import datetime
from django.utils import timezone
from catalog.forms import RenewBookForm

# La filosofía para probar sus formularios es la misma que para probar sus modelos; necesita probar cualquier cosa que haya codificado o que especifique su diseño, pero no el comportamiento del marco subyacente y otras bibliotecas de terceros.
# esto significa que debe probar que los formularios tienen los campos que desea y que estos se muestran con las etiquetas y el texto de ayuda apropiados. 
# No necesita verificar que Django valide el tipo de campo correctamente (a menos que haya creado su propio campo personalizado y validación), es decir, no necesita probar que un campo de correo electrónico solo acepta correos electrónicos. 
# Sin embargo, deberá probar cualquier validación adicional que espera que se realice en los campos y cualquier mensaje que genere su código para detectar errores.

# Por ejemplo, nuestro formulario para renovar libros. Esto tiene solo un campo para la fecha de renovación, que tendrá una etiqueta y un texto de ayuda que necesitaremos verificar.

class RenewBookFormTest(TestCase):

    # probamos que los campos label y help_text sean los correctos. Tenemos que acceder al campo usando el diccionario de campos

    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        # tenemos que probar si el valor de la etiqueta es None, porque aunque Django mostrará la etiqueta correcta, devuelve None si el valor no está explícitamente establecido.
        self.assertTrue(form.fields['renewal_date'].label == None or form.fields['renewal_date'].label == 'renewal date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(form.fields['renewal_date'].help_text,'Enter a date between now and 4 weeks (default 3).')

    # El resto de las funciones prueban que el formulario es válido para fechas de renovación justo dentro del rango aceptable e inválido para valores fuera del rango. 
    # Tenga en cuenta cómo construimos valores de fecha de prueba alrededor de nuestra fecha actual (datetime.date.today()) usando datetime.timedelta() (en este caso especificando un número de días o semanas). 
    # Luego simplemente creamos el formulario, pasamos nuestros datos y probamos si es válido.

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        # usar una aserción para verificar si el formulario es invalido basandose en la información envíada
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.now() + datetime.timedelta(weeks=4)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())
