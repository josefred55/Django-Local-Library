from django.test import TestCase
from catalog.models import Author

# Archivo de prueba patra nuestros modelos definidos en models.py. 
# debemos probar todo lo que sea parte de nuestro diseño o que esté definido por el código que hayamos escrito, pero no las bibliotecas / código que ya haya probado Django o el equipo de desarrollo de Python.

# Por ejemplo, consideremos el modelo de Author. Aquí deberíamos probar las etiquetas para todos los campos (nombre, appelido, etc), porque aunque no hemos especificado explícitamente la mayoría de ellos, tenemos un diseño basado en un modo específico que deberían tener estos valores. 
# Si no probamos los valores, entonces no sabemos que las etiquetas de los campos tienen sus valores deseados. De manera similar, aunque confiamos en que Django creará un campo de la longitud especificada, vale la pena especificar una prueba para esta longitud para asegurarse de que se implementó según lo planeado.

# derivamos nuestra clase de prueba (que va a probar el modelo de author) de TestCase
class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Configurar objetos no modificados utilizados por todos los métodos de prueba
        Author.objects.create(first_name='Big', last_name='Bob')

    # Las pruebas de campo verifican que los valores de las etiquetas de campo (verbose_name) y que el tamaño de los campos de caracteres sean los esperados. 
    # Una cosa a tener en cuenta es que No podemos obtener verbose_name directamente usando author.first_name.verbose_name, porque author.first_name es una cadena (no un identificador del objeto first_name que podemos usar para acceder a sus propiedades). 
    # En su lugar, necesitamos usar el atributo _meta del autor para obtener una instancia del campo y usarlo para consultar la información adicional.
    # Todos estos métodos tienen nombres descriptivos y siguen el mismo patrón

    def test_first_name_label(self):
        author=Author.objects.get(id=1)  # Obtener un objeto de autor para probar
        field_label = author._meta.get_field('first_name').verbose_name # Obtenga los metadatos para el campo requerido y utilícelos para consultar los datos del campo requerido
        self.assertEquals(field_label,'first name') # Compare el valor con el resultado esperado

    def test_last_name_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label,'last name')

    def test_language_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('language').verbose_name
        self.assertEquals(field_label,'language')  

    def test_date_of_birth_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label,'date of birth')

    def test_date_of_death_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label,'Died')

    def test_first_name_max_length(self):
        author=Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length,100)

    def test_last_name_max_length(self):
        author=Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length,100)

    def test_language_max_length(self):
        author=Author.objects.get(id=1)
        max_length = author._meta.get_field('language').max_length
        self.assertEquals(max_length,30)

    # También necesitamos probar nuestros métodos personalizados. 
    # Básicamente, estos simplemente verifican que el nombre del objeto se construyó como esperábamos usando el formato "Apellido", "Nombre", 
    # y que la URL que obtenemos para un elemento Autor es como esperábamos.

    def test_object_name_is_last_name_comma_first_name(self):
        author=Author.objects.get(id=1)
        expected_object_name = '%s %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object_name,str(author))

    def test_get_absolute_url(self):
        author=Author.objects.get(id=1)
        #Esto también fallará si la urlconf no está definida.
        self.assertEquals(author.get_absolute_url(),'/catalog/author/1')
