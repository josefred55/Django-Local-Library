from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# necessary imports for our form class
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm

# vamos a usar vistas de edición genéricas para crear páginas para agregar funcionalidad para crear, editar y eliminar registros de Author de nuestra libreria
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Una vista es una función que procesa una consulta HTTP, trae datos desde la base de datos cuando los necesita, 
# genera una página HTML renderizando estos datos unando una plantilla HTML, y luego retorna el HTML en una respuesta HTTP para ser mostrada al usuario. 
# La vista del índice sigue este modelo
# extrae información sobre cuantos Book, BookInstance, BookInstance disponibles y registros Author tenemos en la base de datos, y los pasa a una plantilla para mostrarlos.

def index(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales, como de los libros y las instancias de cada uno
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_instances_available=BookInstance.objects.filter(status__exact='a').count() # Cuenta los Libros disponibles (los filtramos por: status = 'a')
    num_authors=Author.objects.count()  # El 'all()' esta implícito por defecto.
    num_genres=Genre.objects.count()
    num_books_with_the=Book.objects.filter(title__icontains='the').count() #this will count only the books that contain the subtring 'the'. case insentive

    # Numero de visitas a esta viissta, como está contado en la variable de sesión.
    # request.session.get es para obtener un valor dentro de la sesión que tenga el nombre que se coloca en el primer parámetro
    # si no existe ese dato en la sesión, lo crea y le da un valor de 0, como establece el segundo parametro
    # y cada vez que se recibe una solicitud a la pagina de index, o se llama esta función, que es igual, se incrementa el valor por 1
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # la información de la sesión se guarda automáticamente, porque Django solo guarda información en la base de datos de sesión y envía la cookie de sesión al cliente cuando la sesión ha sido modificada (asignada) o eliminada. 
    # Si estás actualizando algún dato usando su clave de sesión no hay que preocuparse por esto. esto solo funciona al cambiar un dato de la sesión, y no DENTRO de ella, ver abajo

    # Renderiza la plantilla HTML index.html, envíando los datos obtenidos de los modelos en un diccionario
    # la función render va a buscar la plantilla en el directorio templates o en otras palabras espera encontrar el archivo: /locallibrary/catalog/templates/index.html
    return render(
        request, #HTTP
        'index.html', #Plantilla
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors, 'num_genres':num_genres, 'num_books_with_the':num_books_with_the, 'num_visits':num_visits}, # Datos
    )

# para la página de vista de la lista de los libros en lugar de una función de vista regular se va a usar una vista de lista genérica basada en clases (ListView) — una clase que hereda una vista ya existente que toma como módelo, por eso es generica.
# esta ya implementa la mayoría de la funcionalidad que necesitamos, y sigue la práctica adecuada de Django, seremos capaces de crear una vista de lista más robusta con menos código, menos repetición, y por último menos mantenimiento.

# Con esto ya La vista genérica consultará a la base de datos para obtener todos los registros del modelo especificado (Book) y renderizará una plantilla ubicada en /locallibrary/catalog/templates/catalog/book_list.html (que crearemos más abajo). 
# Dentro de la plantilla puedes acceder a la lista de libros mediante la variable de plantilla llamada object_list O book_list (esto es, genéricamente, "nombre_del_modelo_list").

class BookListView(generic.ListView):
    model = Book # obtener todos los datos del modelo book de la base de datos
    paginate_by = 3 # para añadir paginación los items deben tener un orden definido, ya sea aquí mismo en al vista o en la clase del módelo, como hice yo
    context_object_name = 'book_list'   # su propio nombre para la lista como variable de plantilla
    template_name = 'books/my_arbitrary_template_name_list.html'  # Especifique su propio nombre/ubicación de plantilla
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Consigue 5 libros que contengan el título de guerra, ajustando el queryset con filter.

# vista detallada de un libro en específico basado también en vistas genéricas (esta vez no es de listas sino de detalle como el nombre indica)
#  con estas líneas Lo único que necesitas hacer ahora es crear una plantilla llamada /locallibrary/catalog/templates/catalog/book_detail.html, 
# y la vista enviará la información en la base de datos para el registro del libro específico, extraído por el mapeador URL. 
# Dentro de la plantilla puedes acceder a la lista de libros mediante la variable de plantilla llamada object o book (esto es, genéricamente, "el_nombre_del_modelo").
    
class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

    # envíamos información adicional para que la página de vista reciba la lista de libros escritos por el autor actual
    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['book_list'] = Book.objects.filter(author=self.object).all
        return context

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros prestados al usuario actual. Estamos usando LoginRequiredMixin para solo permitir el acceso a los usuarios logeados
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    # editar el queryset para obtener en el contexto solo los libros que en su campo borrower tengan como valor el usuario actual
    # Nótese que "o" es el código almacenado para "on loan" (en alquiler) y vamos a ordenar por la fecha due_back para que los elementos más antiguos se muestren primero.

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    
class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros todos los libros prestados de la biblioteca con su respectivo prestatario. 
    Estamos usando PermissionRequiredMixin para solo permitir el acceso a los bibliotecarios
    """

    # este permiso se va a añadir al contexto de la vista, y lo vamos a usar en la plantilla para decir que, solo los que tengan dicho permiso pueden acceder a la página
    # recordemos que, este permiso lo creamos en el atributo meta del modelo de book, y se lo dimos al grupo de librarians en el sitio de administración al crearlo
    # así que quien forme parte de ese grupo tendrá dicho permiso

    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    # filtrar todos los libros que tengan de status "on loan"

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
    
# restringir el acceso a la vista a los bibliotecarios. Probablemente deberíamos crear un nuevo permiso en BookInstance ("can_renew"),
# pero para simplificar las cosas aquí solo usamos el decorator @permission_required con nuestro existente permiso can_mark_returned.
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """

    # usamos el argumento pk (id envíado por la url) en get_object_or_404() para obtener el actual BookInstance (si esto no existe, la vista se cerrará inmediatamente y la página mostrará un error "no encontrado").
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # la vista debe presentar el formulario predeterminado cuando se llama por primera vez y luego volver a representarlo con mensajes de error si los datos no son válidos,
    # o procesar los datos y redirigirlos a una nueva página si los datos son válidos. Por tanto, la vista debe saber si la página se está llamando por primera vez
    # para presentar el form o no. Si el método http usado fue POST, sabemos que ha sido enviada información al servidor, así identificamos una solicitud de formulario

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Creamos un objeto Form (con la clase que definimos en forms.py) y le añadimos la información mandada en los datos de la solicitud del usuario, (los cuales están en request.POST) (este proceso se llama binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid. (Si el formulario no es válido llamamos render() de nuevo, pero esta vez el valor del formulario pasado en el contexto incluirá mensajes de error)
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the bookinstance model due_back field )
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redireccionar a otra url para indicar "éxito", aquí vamos a redireccionar a la página de todos los libros prestados 
            return HttpResponseRedirect(reverse('all-borrowed') )

    # Si no se trata de una solicitud POST, creamos el formulario predeterminado (con la clase de forms.py )que pasa un valor inicial (initial) recomendado para el campo renewal_date (el valor es 3 semanas desde la fecha actual).
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    # creamos la página HTML, especificando la plantilla y un contexto que contiene nuestro formulario. En este caso, el contexto también incluye nuestro BookInstance, que usaremos en la plantilla para proporcionar información sobre el libro que estamos renovando.
    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


# El algoritmo de manejo de formularios que utilizamos en nuestro ejemplo de vista de funciones anterior representa un patrón extremadamente común en las vistas de edición de formularios. 
# Django extrae gran parte de esta "plantilla" para ti, para crear vistas de edición genéricas ( generic editing views ) para crear, editar y eliminar vistas basadas en modelos.
# No solo manejan el comportamiento de "vista", sino que crean automáticamente la clase de formulario (un ModelForm) para tu modelo.
# las plantillas de las vistas "create" y "delete" utilizan la misma plantilla perdeterminadamente, basandose su nombre en el del modelo creado o editado: author_name_form.html aunque esto se puede mofidicar con el atributo template_name_suffix

class AuthorCreate(PermissionRequiredMixin, CreateView):
    # especificamos el modelo asociado a la vista, los campos a mostrar en el fórmulario (aquí se mostraran todos) para las vistas de crear y actualizar
    permission_required = 'catalog.can_modify'
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_modify'
    model = Author
    # También puede especificar valores iniciales para cada uno de los campos utilizando un diccionario de pares nombre_campo / valor (aquí establecemos arbitrariamente la fecha de fallecimiento para fines de demostración; ¡es posible que desee eliminar eso!).
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_modify'
    model = Author
    # el atributo sucess_url en las dos vistas anteriores por defecto van a redirigir a la misma página del modelo que ha sido creado o editado, que en este caso será la vista detallada del autor
    # pero aquí especificamos una ubicación alternativa de redireccionamiento declarando explícitamente el parámetro success_url. ya que al estar literalmente eliminando al autor no tiene un valor por defecto
    # aunque, valga la redundancia, por defecto al eliminar una instancia de un modelo, django va a esperar encontrar una plantilla para confirmar la eliminación del aautor: authorname_confirm_delete.html
    # reverse_lazy() is a lazily executed version of reverse(), se usa aquí porque estamos proporcionando una URL a un atributo de vista basado en clases.
    success_url = reverse_lazy('authors')

# lo mismo pero con los libros
    
class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_modify'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_modify'
    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_modify'
    model = Book
    success_url = reverse_lazy('books')



    

# ejemplo de los permisos en las vistas
# Los permisos pueden ser probados en una vista de función usando el decorador permission_required o en una vista basada en clases usando el PermissionRequiredMixin.
# El patrón y el comportamiento son los mismos que para la autenticación de inicio de sesión, aunque desde luego podrías razonablemente tener que añadir múltiples permisos.
    
# decorador de permisos para vistas de funciones
    
# from django.contrib.auth.decorators import permission_required

# @permission_required('catalog.can_mark_returned')
# @permission_required('catalog.can_edit')
# def my_view(request):
#     ...
    
#"Mixin" de permisos requeridos para vistas basadas en clases:

# from django.contrib.auth.mixins import PermissionRequiredMixin

# class MyView(PermissionRequiredMixin, View):
#     permission_required = 'catalog.can_mark_returned'
#     # O múltiples permisos
#     permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
#     # Tenga en cuenta que 'catalog.can_edit' es solo un ejemplo: La aplicación no tiene ese permiso


# la forma más facil para restringir el acceso a tus funciones es aplicar el decorador login_required a tu función de vista, como se muestra más abajo. 
# Si el usuario ha iniciado sesión entonces tu código de vista se ejecutará como normalmente lo hace.
# Si el usuario no ha iniciado sesión, se redirigirá a la URL de inicio de sesión definida en tu configuración de proyecto (settings.LOGIN_URL), 
# pasando el directorio absoluto actual como el parámetro URL next. Si el usuario tiene éxito en el inicio de sesión entonces será devuelto a esta página, pero esta vez autenticado.

# @login_required
# def my_view(request):
#     ...
    
#esto también se puede lograr con request.user.is_authenticated pero el decorador es mas conveniente

# la forma más fácil de restringir el acceso a los usuarios que han iniciado sesión en tus vistas basadas en clases es extender de LoginRequiredMixin.
# Esto tiene exactamente el mismo comportamiento de redirección que el decorador login_required.
# También puedes especificar una localización alternativa para redirigir al usuario si no están autenticados (login_url), 
# y un nombre de parámetro URL en lugar de "next" para insertar el directorio absoluto actual (redirect_field_name).

# class MyView(LoginRequiredMixin, View):
#     login_url = '/login/'
#     redirect_field_name = 'redirect_to'




# algo a tener en cuenta es que si el registro solicitado (como book por ejemplo) no existe, la vista de detalle genérica basada en clases lanzará automáticamente por tí una excepción de tipo Http404.
# como se podría implementar esto, si si no estuvieras usando la vista de detalle genérica basada en clases. sino que la estuvieramos implementando como una función:
    
# def book_detail_view(request,pk):
#     try:
#         book_id=Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         raise Http404("Book does not exist")

#     #book_id=get_object_or_404(Book, pk=pk)

#     return render(
#         request,
#         'catalog/book_detail.html',
#         context={'book':book_id,}
#     )



# algunas cosas que se pueden hacer con vistas genericas en clases:

# aunque el queryset también puede ser sobreescrito para que sea un poco más simple que ajustarlo con filter, aunque no hay mucho beneficio real de ello
# def get_queryset(self):
#     return Book.objects.filter(title__icontains='war')[:5] 

# Podríamos también sobreescribir get_context_data() con el objeto de pasar variables de contexto adicionales a la plantilla (ej. la lista de libros se pasa por defecto, por eso no hay que especificarla).
# El fragmento de abajo muestra cómo añadir una variable llamada "some_data" al contexto (la misma estaría entonces disponible como una variable de plantilla).}
# def get_context_data(self, **kwargs):
#     # Primero obtener el contexto existente desde nuestra superclase.
#     context = super(BookListView, self).get_context_data(**kwargs)
#     # Luego añadir tu nueva información de contexto.
#     context['some_data'] = 'Estos son solo algunos datos'
#     # Luego devolver el nuevo contexto (actualizado).
#     return context



# ejemplo de las sesiones 
# El atributo session es un objeto tipo diccionario que puedes leer y escribir tantas veces como quieras en tu vista, modificándolo como desees. 
# Puedes realizar todas las operaciones normales de diccionario, incluyendo eliminar toda la información, probar si una clave está presente, iterar a través de la información, etc. 
# Sin embargo, la mayor parte del tiempo solo usarás la API estándar de "diccionario" para recuperar y establecer valores.
    
# Obtener un dato de la sesión por su clave (ej. 'my_car'), generando un KeyError si la clave no existe
# my_car = request.session['my_car']

# # Obtener un dato de la sesión, estableciendo un valor por defecto ('mini') si el dato requerido no existe
# my_car = request.session.get('my_car', 'mini')

# # Asignar un dato a la sesión
# request.session['my_car'] = 'mini'

# # Eliminar un dato de la sesión
# del request.session['my_car']
    

# Django solo guarda información en la base de datos de sesión y envía la cookie de sesión al cliente cuando la sesión ha sido modificada (asignada) o eliminada. 
# Si estás actualizando algún dato usando su clave de sesión no hay que preocuparse por esto:
    
# Esto es detectado como un cambio en la sesión, así que la información de la sesión es guardada.
# request.session['my_car'] = 'mini'

# Si estás actualizando algún dato dentro de la información de sesión, Django no reconocerá que has hecho un cambio en la sesión y guardado la información 
# (por ejemplo, si fueras a cambiar el dato "wheels" dentro de tu dato "my_car", como se muestra abajo). 
# En este caso, necesitarás marcar explícitamente la sesión como que ha sido modificada.
    
# Objeto de sesión no directamente modificada, solo información dentro de la sesión. ¡Cambios no guardados!
# request.session['my_car']['wheels'] = 'alloy'

# Establecer la sesión como modificada para forzar a que se guarden los cambios.
# request.session.modified = True
