from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

#importar los modelos que creamos en models.py, así es como los agregamos a la aplicación

#admin.site.register(Book)
#admin.site.register(Author)
#admin.site.register(BookInstance)

admin.site.register(Genre) #el género no require que le modifiquemos el modo de presentacion porque solo tiene un campo, sería inútil.

# A veces puede tener sentido el añadir registros asociados al mismo tiempo. 
# Por ejemplo, puede tener sentido el tener información tanto de un libro como de las copias específicas que has adquirido del mismo, ambos en la misma página.
# Puedes hacerlo declarando inlines, de tipo TabularInline (diseño horizontal) o StackedInline (diseño vertical, tal como el diseño de modelo por defecto).
# Gracias a eso, al estar viendo la información de un libro, vamos a poder ver al final de la página todas las instancias "físicas" de ese libro

# vamos a usar esto para mostrar los libros que tiene cada autor al final de la página de la vista detallada del autor
class BooksInLine(admin.TabularInline):
    model = Book
    fields = ['title', 'summary', 'genre']
    extra = 0

class AuthorAdmin(admin.ModelAdmin):
    # sin esto, nuestra locallibrary solo mostrara el titulo de los libros usando su metodo __str__. Pero esto puede traer duplicados en una lista grande
    # Para diferenciarlos, o simplemente para mostrar información más interesante sobre cada autor, se puede usar list_display para añadir otros campos que se vean al listarlos.
    # como se puede ver, los argumentos que necesita son los nombres de campos del modelo
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')

    # el atributo de arriba controla todo sobre los campos que se muestran al desplegar la lista de elementos de se modelo, y el de abajo controla los campos que se muestran en el formulario 

    # Podemos cambiar el orden en que se muestran los elementos, que elementos se muestran o no, e incluso la forma en que se muestran (vertical u horizontal)
    # El atributo fields lista solo los campos que se van a desplegar en el formulario (es decir, al editar el modelo o añadir uno)
    # Los campos se despliegan en vertical por defecto, pero se desplegarán en horizontal si los agrupas en una tupla
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    inlines = [BooksInLine]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0    # para que no se muestren instancias extras del libro vacías

@admin.register(Book) # la expresión @register registra los modelos (hace exactamente lo mismo que admin.site.register())
class BookAdmin(admin.ModelAdmin):
    #no podemos especificar directamente el modelo del genero porque es un manytomanyfield y segun django esto seria muy costoso para acceder a la base de datos
    #por eso vamos a usar un método (el cual vamos a definir en el modelo de book)para obtener la información como una cadena
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')

    # Podemos filtrar los ítems que se despliegan. Esto se hace listando campos del módelo en el atributo list_filter.
    # Entonces solo se mostraran los libros que cumplan los requisitos escogidos de ciertos campos
    list_filter = ('status', 'due_back')

    # Puedes añadir "secciones" para agrupar información relacionada del modelo dentro del formulario de detalle, usando el atributo fieldsets.
    # la forma en que la definimos hace que los campos esten separados en dos secciones. una sección sin nombre (none) que muestra el libro, su imprint y id
    # y la segunda sección que tiene el nombre de disponibilidad, muestra los campos  relacionados con esa información

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower') # el colocar un borrower en los campos a mostrar en la pagina de admin va a hacer que podamos asignar un user a un bookInstance
        }),
    )
