from django.test import TestCase

from catalog.models import Author
from django.urls import reverse

# Para validar nuestro comportamiento de vista, usamos la prueba Django Cliente. Esta clase actúa como un navegador web ficticio que podemos usar para simular solicitudes GET y POST en una URL y observar la respuesta. 
# Podemos ver casi todo sobre la respuesta, desde HTTP de bajo nivel (encabezados de resultados y códigos de estado) hasta la plantilla que estamos usando para representar el HTML y los datos de contexto que le estamos pasando. 
# También podemos ver la cadena de redirecciones (si las hay) y comprobar la URL y el código de estado en cada paso. Esto nos permite verificar que cada vista está haciendo lo que se espera.

# Vamos a comenzar probando la vista de la lista de todos los autores

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Crear 13 autores para pruebas de paginación
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)

    # los métodos de prueba que chequean que la url este en la locación deseada, que se acceda con el nombre correcto, que use la plantilla correcta
    # que la paginación esté bien (que especificamos con el atributo en su clase) y que se listen todos los autores correctamente.
    # Todas las pruebas usan el cliente (perteneciente a la clase derivada de nuestro TestCase) para simular una solicitud GET y obtener una respuesta (resp). 
    # La primera versión verifica una URL específica (nota, solo la ruta específica sin el dominio) mientras que la segunda genera la URL a partir de su nombre en la configuración de URL.
    # Nota como siempre se chequea el status code envíado por la respuesta para verificar que la solicitud GET a la url haya salido bien.

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Obtenga la segunda página y confirme que tiene (exactamente) 3 elementos restantes
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 3)

    # La variable más interesante aquí es resp.context, que es la variable de contexto que la vista pasa a la plantilla. 
    # Esto es increíblemente útil para realizar pruebas, ya que nos permite confirmar que nuestra plantilla obtiene todos los datos que necesita. 
    # En otras palabras, podemos verificar que estamos usando la plantilla deseada y qué datos está obteniendo la plantilla, 
    # lo que contribuye en gran medida a verificar que cualquier problema de representación se deba únicamente a la plantilla.
        

# vamos a probar una vista que está restringida solo a los usuarios registrados. 
# Por ejemplo, nuestro LoanedBooksByUserListView es muy similar a nuestra vista anterior, pero solo está disponible para los usuarios registrados 
# y solo muestra los registros de BookInstance que el usuario actual tomó prestados, tienen el estado 'en préstamo' y están ordenados como "los más antiguos". primero".
        
# aquí primero usamos SetUp() para crear algunas cuentas de inicio de sesión de usuario y objetos BookInstance (junto con sus libros asociados y otros registros) que usaremos más adelante en las pruebas. 
# Cada usuario de prueba toma prestado la mitad de los libros, pero inicialmente hemos establecido el estado de todos los libros en "mantenimiento". Hemos usado SetUp() en lugar de setUpTestData() porque modificaremos algunos de estos objetos más adelante.
        
import datetime
from django.utils import timezone
from catalog.models import BookInstance, Book, Genre
from django.contrib.auth.models import User #Obligatorio para asignar al usuario como prestatario

class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        #Crear dos usuarios
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        #Crear un libro (para ello primero necesitamos un autor y un género de prueba)
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) #No se permite la asignación directa de tipos de muchos a muchos.
        test_book.save()

        #Crea 30 objetos BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date= timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower=test_user1
            else:
                the_borrower=test_user2
            status='m'
            BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=the_borrower, status=status)

    # Para verificar que la vista redirigirá a una página de inicio de sesión si el usuario no ha iniciado sesión, usamos assertRedirects.
    # Para verificar que la página se muestra para un usuario conectado, primero iniciamos sesión en nuestro usuario de prueba y luego accedemos a la página nuevamente y verificamos que obtengamos un status_code de 200 (éxito).

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "exitosa"
        self.assertEqual(resp.status_code, 200)

        #Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

    # El resto de la prueba verifica que nuestra vista solo devuelve libros que están en préstamo a nuestro prestatario actual.

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        #CComprueba que inicialmente no tenemos ningún libro en lista (ninguno en préstamo)
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual( len(resp.context['bookinstance_list']),0)

        #Ahora cambia todos los libros para que estén en préstamo
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status='o'
            copy.save()

        #Comprueba que ahora tenemos libros prestados en la lista
        resp = self.client.get(reverse('my-borrowed'))
        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        #Confirma que todos los libros pertenecen a testuser1 y están en préstamo
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        #Cambiar todos los libros para que estén en préstamo
        for copy in BookInstance.objects.all():
            copy.status='o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        #Confirma que de los artículos, solo se muestran 10 debido a la paginación.
        self.assertEqual( len(resp.context['bookinstance_list']),10)

        last_date=0
        for copy in resp.context['bookinstance_list']:
            if last_date==0:
                last_date=copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)



# Probar vistas con formularios es un poco más complicado que en los casos anteriores, porque necesita probar más rutas de código: 
# visualización inicial, visualización después de que la validación de datos haya fallado y visualización después de que la validación haya tenido éxito. 
# La buena noticia es que usamos el cliente para realizar pruebas casi exactamente de la misma manera que lo hicimos para las vistas de solo visualización.

from django.contrib.auth.models import Permission # Requerido para otorgar el permiso necesario para establecer un libro como devuelto.

# Tendremos que probar que la vista solo está disponible para los usuarios que tienen el permiso can_mark_returned y que los usuarios son redirigidos a una página de error HTTP 404 si intentan renovar una BookInstance que no existe. 
# Deberíamos verificar que el valor inicial del formulario esté iniciado con una fecha de tres semanas en el futuro y que, si la validación tiene éxito, se nos redirija a la vista "todos los libros prestados". Como parte de la verificación de las pruebas de falla de validación, 
# también verificaremos que nuestro formulario envíe los mensajes de error apropiados.

class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        # crear un usuario sin permisos y otro con permisos
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        
        test_user2 = User.objects.create_superuser(username='testuser2', password='12345')
        test_user2.save()
        
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # No se permite la asignación directa de tipos de muchos a muchos.
        test_book.save()

        #Cree un objeto BookInstance para test_user1
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

        #Cree un objeto BookInstance para test_user2
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')

    # Estos métodos de abajo comprueban que solo los usuarios con los permisos correctos (testuser2) pueden acceder a la vista. Verificamos todos los casos: 
    # cuando el usuario no ha iniciado sesión, cuando un usuario ha iniciado sesión pero no tiene los permisos correctos, cuando el usuario tiene permisos pero no es el prestatario (debería tener éxito) 
    # y qué sucede cuando intenta acceder a una BookInstance que no existe. También comprobamos que se utiliza la plantilla correcta.
        
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        #Revisar manualmente la redirección (no se puede usar assertRedirect, porque la URL de redirección es impredecible)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )

        #Revisar manualmente la redirección (no se puede usar assertRedirect, porque la URL de redirección es impredecible)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}) )

        #Comprobar que nos permita iniciar sesión: este es nuestro libro y tenemos los permisos correctos.
        self.assertEqual( resp.status_code,200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )

        #Comprobar que nos deja iniciar sesión. Somos bibliotecarios, por lo que podemos ver cualquier libro de usuarios.
        self.assertEqual( resp.status_code,200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4() #¡Es improbable que el UID coincida con nuestra instancia de libro!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}) )
        self.assertEqual( resp.status_code,404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        self.assertEqual( resp.status_code,200)

        #Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

    # Esto comprueba que la fecha inicial del formulario es tres semanas en el futuro. 
    # Observe cómo podemos acceder al valor del valor inicial del campo de formulario

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        self.assertEqual( resp.status_code,200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future )

    # La siguiente prueba verifica que la vista redirige a una lista de todos los libros prestados si la renovación tiene éxito. Lo que difiere aquí es que, por primera vez, mostramos cómo puede "POST" datos usando el cliente. 
    # La publicación datos es el segundo argumento de la función de post y se especifica como un diccionario de clave/valores.

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        # nota como envíamos la fecha válida como respuesta al formulario como segundo argumento en post
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future} )
        self.assertRedirects(resp, reverse('all-borrowed') )

    # Estas ultimas funciones nuevamente prueban las solicitudes 'POST', pero en este caso con fechas de renovación no válidas. 
    # Usamos assertFormError() para verificar que los mensajes de error sean los esperados.

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':date_in_past} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':invalid_date_in_future} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

class AuthorCreateViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        
        test_user2 = User.objects.create_superuser(username='testuser2', password='12345')
        test_user2.save()

    # Metodos de prueba para redireccionar si el usuario no ha iniciado sesión, si la tiene pero no tiene permisos, y si si tiene servicios

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('author-create'))
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_forbid_access_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual( resp.status_code,403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author-create'))

        self.assertEqual( resp.status_code,200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual( resp.status_code,200)

        #Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/author_form.html')

    def test_form_has_correct_date_of_death(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author-create'))

        # revisar que la fecha de muerte inicial este correcta
        predeterminada_date_of_death = '05/01/2018'
        self.assertEqual(resp.context['form'].initial['date_of_death'],predeterminada_date_of_death)

    # comprobar que al completarse el formulario con exito redirija a la vista detallada del autor creado

    def test_redirect_to_author_detail_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.post(reverse('author-create'), {'first_name': 'John', 'last_name': 'Malkovich', 'language': 'English'})

        newly_created_author = Author.objects.get(first_name='John', last_name='Malkovich', language='English')
        self.assertRedirects(resp, reverse('author-detail', kwargs={'pk':newly_created_author.pk,}))








