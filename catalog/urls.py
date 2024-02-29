from django.urls import path, include

from . import views

# Éste es donde añadimos nuestros patrones a medida que construimos la aplicación.
# Al abrir la pagina web, como sabemos la url raíz d ela página nos va a redirigir al submodule /catalog/ dentro de esa url raíz
# Esto para que al entrar a la url raíz del proyecto esta redirija al usuario a la url base de nuestra aplicación que es la que queremos que se eva
# Pero si no tenemos ninguna url definida aquí (dentro de urlpatterns) django nos va a dar un error, porque no tiene ninguna url que mostrar

urlpatterns = [
    # Esta función path() define una cadena vacía (''), y una función vista que será llamada si el patrón es detectado (views.index — una función llamada index() en views.py).
    # Esta cadena que parece vacía, debe coincidir con la cadena envíada por include, si está vacía significa que la url terminó en /catalog/, pues es la parte que coincide y django la asume
    # por tanto esta sub-url sería el index de catalog porque no hay nada después de /catalog/
    # el parametro name, que identifica unicamente a esta url se puede usar para crear dinamicamente otra url usando su valor con jinja, es decir referirnos a este path dentro de una plantilla
    path('', views.index, name='index'),

    # si la url coincide con /books (que originalmente debe ser /catalog/books/) se llamará a la función de vista que servirá una página que muestre todos los libros
    # La función de vista tiene un formato diferente al anterior — eso es porque esta vista será en realidad implementada como una clase. 
    # Heredaremos desde una función de vista genérica existente que ya hace la mayoría de lo que queremos que esta función de vista haga, en lugar de escribir una nueva desde el inicio.
    # esto es similar a como tenemos una platilla html base la cual podemos usar en todas las otras plantillas en lugar de reescribirla desde cero
    path('books/', views.BookListView.as_view(), name='books'),

    # La página de detalle de libro desplegará información sobre un libro específico, a la que se accede usando la URL catalog/book/<id> (donde <id> es la clave primaria para el libro). 
    # Además de los campos en el modelo Book (autor, resumen, etc), listaremos también los detalles de las copias disponibles (BookInstances) incluyendo su estado, fecha de devolución esperada, edición e id.
    # el patrón URL utiliza una sintaxis especial para capturar el id específico del libro que queremos ver. 
    # los corchetes angulares definen la parte de la URL a capturar (<int:pk>), encerrando el nombre de la variable que la vista puede utilizar para acceder a los datos capturados. 
    # Por ejemplo, <algo>, capturará el patrón marcado y pasará el valor a la vista como una variable "algo". Adicionalmente se peude añadir una etiqueta que defina el tipo de dato de la variable (en este caso, int)
    # entonces En este caso utilizamos '<int:pk>' para capturar el id del libro, que debe ser una cadena con un formato especial y pasarlo a la vista como un parámetro llamado pk (abreviatura de primary key).
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    # también se puede especificar un path de url con expresiones regulares, esto puede ser util para que el el filtrado del path solo acepte cadenas con un cierto número de carácteres, por ejemplo.
    # lo más básico es que las RE se declaran así: r'<tu expresión regular va aquí>'). Para ver parte del sintaxis ver tutorial django parte 6 mdn

    # Esta de aquí abajo es la RE que podría reemplazar nuestro mapeador url de arriba. Concide con una cadena que tiene book/ al inicio de la línea (^book/), luego tiene uno o más dígitos (\d+), y luego termina (sin ningún caracter que no sea un dígito antes del marcador de fin de línea).
    # También captura todos los dígitos (?P<pk>\d+) y los envía a la vista como un parámetro llamado 'pk'. ¡Los valores capturados siempre se envían como cadena!
    # Por ejemplo, esto coincidiría con book/1234, y enviaría una variable pk='1234' a la vista.

    # re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail')

    # la pagina de lista de los autores
    path('authors/', views.AuthorListView.as_view(), name='authors'), 

    #la pagina de vista detallada de los autores
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

    # la pagina de vista que va a mostrar la lista de libros que tiene el user alquilado usando vista génerica basada en clases para listas
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),

    # pagina de vista solo para bibliotecarios que muestra todos los libros que han sido prestados y sus prestatarios respectivos
    path('allborrowed/', views.AllLoanedBooksListView.as_view(), name='all-borrowed'),

    # pagina que permitirá a los bibilotecarios renovar los libros prestados usando un django form
    # La configuración de URL redirigirá las URL con el formato /catalog/book/<bookinstance id>/renew/ a la función llamada renew_book_librarian() en views.py, 
    # y envia el id de BookInstance como parametro llamado pk.
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),

    # configuración de url de las vistas de edición genéricas para crear, editar y eliminar autores
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

