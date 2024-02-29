from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User
import uuid # Requerida para las instancias de libros únicos
from datetime import date

# Las aplicaciones web de Django acceden y administran los datos a través de objetos de Python a los que se hace referencia como modelos. 
# Los modelos definen la estructura de los datos almacenados, incluidos los tipos de campo y los atributos de cada campo, como su tamaño máximo, 
# valores predeterminados, lista de selección de opciones, texto de ayuda para la documentación, texto de etiqueta para formularios, etc. 
# La definición del modelo es independiente de la base de datos subyacente. puede elegir una de entre varias como parte de la configuración de su proyecto. 
# Una vez que haya elegido la base de datos que desea usar, no necesita hablar directamente con ella. Simplemente escriba la estructura de su modelo y algo de código, 
# y Django se encargará de todo el trabajo sucio, al comunicarse con la base de datos por usted.

# Create your models here.

class Genre(models.Model):
    """
    Modelo que representa un género literario (p. ej. ciencia ficción, poesía, etc.).
    """
    # el campo name lo usaremos para describir el género literario con charfield.
    # Este campo tiene un tamaño máximo (max_length) de 200 caracteres y, además, posee un help_text.
    name = models.CharField(max_length=200, help_text="Ingrese el nombre del género (p. ej. Ciencia Ficción, Poesía Francesa etc.)")

    def __str__(self):
        """
        Cadena que representa a la instancia particular del modelo (p. ej. en el sitio de Administración)
        """
        return self.name
    

class Book(models.Model):
    """
    Modelo que representa un libro (pero no un Ejemplar específico).
    """
    # campos:

    title = models.CharField(max_length=200)

    language = models.CharField(max_length=30)

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # ForeignKey, ya que un libro tiene un solo autor, pero el mismo autor puede haber escrito muchos libros.
    # 'Author' es un string, en vez de un objeto, porque la clase Author aún no ha sido declarada.
    # el parámetro null=True, permite a la base de datos almacenar null si el autor no ha sido seleccionado, y on_delete=models.SET_NULL, que pondrá en null el campo si el registro del autor relacionado es eliminado de la base de datos.

    summary = models.TextField(max_length=1000, help_text="Ingrese una breve descripción del libro")

    isbn = models.CharField('ISBN',max_length=13, help_text='13 Caracteres <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    genre = models.ManyToManyField(Genre, help_text="Seleccione un genero para este libro")
    # ManyToManyField, porque un género puede contener muchos libros y un libro puede cubrir varios géneros.
    # La clase Genre ya ha sido definida, entonces podemos especificar el objeto arriba, y no una string.

    #métodos

    def __str__(self):
        """
        String que representa al objeto Book, para referirnos a el cuando se requiera
        """
        return self.title


    def get_absolute_url(self):
        """
        Devuelve el URL a una instancia particular de Book. 
        este URL que puede ser usado para acceder al detalle de un registro particular 
        para que esto funcione, debemos definir un mapeo de URL (la función path) que tenga el nombre book-detail (el argumento name) y una vista y una plantilla asociadas a él
        """
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        Esto crea una cadena con los tres primeros valores del campo genre (si existen) y crea una short_description
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    
    display_genre.short_description = 'Genre'

    class Meta:
        ordering = ["title"]

        # así se específican los permisos asociados a un módelo. Puedes especificar tantos permisos como necesites en una tupla, 
        # cada permiso está definido a sí mismo en una tupla anidada que contiene el nombre del permiso y el valor mostrado del mismo. 
        # Por ejemplo, podríamos definir un permiso para permitir a un usuario marcar un libro que ya ha sido devuelto, como se muestra abajo.
        # Podríamos asignar este permiso a un grupo bibliotecario "Librarian" en el sitio de Administración.
        permissions = (("can_mark_returned", "Set book as returned"),)
        permissions = (("can_modify", "Create, Update and Delete books"),)

        # Los permisos del usuario actual están almacenados en una variable de plantilla llamada {{ perms }}. 
        # Puedes comprobar si el usuario actual tiene un permiso particular usando el nombre de variable específico con la "app" asociada en Django — 
        # ej. {{ perms.catalog.can_mark_returned }} será True (cierto) si el usuario tiene el permiso, y False (falso) en otro caso.


class BookInstance(models.Model):
    """
    Modelo que representa una copia específica de un libro (i.e. que puede ser prestado por la biblioteca). No representa al libro original, pues ese está definido por Book 
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="ID único para este libro particular en toda la biblioteca") # UUIDField es usado para establecer el campo id como una primary_key, aquella que no se repite en toda la base de datos
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True) # ForeignKey para identificar el Libro asociado (cada libro puede tener muchas copias, pero una copia solo puede tener un Book). OJO: cambié "Book" por Book, porque me parece que lo lógico es que al ya existir el módelo del libro nos deberíamos poder referir a el
    # el valor de on_delete es la acción a tomar cuando el objeto referenciado es eliminado (que el libro referido por la bookinstance se elimine), en este caso el valor de cascade va a hacer que al elimianrse el libro también se elimine toda bookinstance que se refiera a este libro
    imprint = models.CharField(max_length=200) #CharField para representar la imprenta (publicación específica) del libro.
    due_back = models.DateField(null=True, blank=True) # DateField es usado para la fecha en la que se espera que el libro este diponible despues de ser prestado o estar en mantenimiento. Este valor puede ser blank o null (ya que no es relevante cuando el libro este disponible).

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    # status es un CharField que define una lista de elección/selección. Como puedes ver, hemos definido una tupla que contiene tuplas de pares clave-valor y los pasamos a los argumentos de choice. 
    # El valor en un par clave/valor es un valor desplegable que el usuario puede seleccionar, mientras las claves son valores que en realidad son guardados en la opción seleccionada. 
    # El valor por defecto de 'm' (maintenance) ya que los libros inicialmente se crearán como no disponibles antes de que esten almacenados en los estantes.

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Estado de disponibilidad del libro') 

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # vamos a hacer posible para los usuarios tener una BookInstance en alquiler (prestado). como podemos ver esto asocia al modelo con un usuario

    class Meta:
        ordering = ["due_back"]


    def __str__(self):
        """
        String para representar el Objeto del Modelo. 
        representa el objeto BookInstance usando una combinación de su id único y el título del Book asociado.
        """
        return f'{self.id} ({self.book.title})'
    
    # vamos a añadir una propiedad que podamos llamar desde nuestras plantillas para decir si una instancia particular de un libro está atrasada.
    # Primeramente verificamos si la fecha due_back está vacía antes de realizar una comparación. 
    # Un campo vacío due_back provocaría a Django arrojar un error en lugar de mostrar la página: los valores vacíos no son comparables.
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    
class Author(models.Model):
    """
    Modelo que representa un autor
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    language = models.CharField(max_length=30)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('author-detail', args=[str(self.id)])


    def __str__(self):
        """
        String para representar el Objeto Modelo
        """
        return f'{self.last_name} {self.first_name}'
    
    class Meta:
        ordering = ['last_name']
        permissions = (("can_modify", "Create, Update and Delete authors"),)


    








    
# # Creación de un nuevo registro usando el constructor del modelo (es decir, vamos a construir un modelo con la clase que se encuentra arriba).
# a_record = (my_field_name="Instancia #1")

# # Guardar el objeto en la base de datos.
# a_record.save()

# # Accesso a los valores de los campos del modelo usando atributos Python.
# print(a_record.id) # Debería devolver 1 para el primer registro, Porque si no has declarado ningún campo como primary_key, al nuevo registro se le proporcionará una automáticamente, con el nombre de campo id, que empezará por 1. 
# print(a_record.my_field_name) # Debería imprimir 'Instancia #1'

# # Cambio de un registro modificando los campos llamando a save() a continuación.
# a_record.my_field_name="Nuevo Nombre de Instancia"
# a_record.save()