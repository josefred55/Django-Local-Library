from django.test import TestCase

# este es un archivo ejemplo sin ninguna utilidad, por eso su nombre está mal escrito a propósito
# en este archivo se ejecutarian pruebas usando django.test.TestCase. Esta clase de prueba crea una base de datos limpia antes de que se ejecuten sus pruebas 
# y ejecuta cada función de prueba en su propia transacción. La clase también posee una prueba Client que puede utilizar para simular la interacción de un usuario con el código en el nivel de vista.

# A menudo, agregará una clase de prueba para cada modelo / vista / formulario que desee probar, con métodos individuales para probar una funcionalidad específica. Esto sería una prueba unitaria
# En otros casos, es posible que desee tener una clase separada para probar un caso de uso específico, con funciones de prueba individuales que prueben aspectos de ese caso de uso 
# (por ejemplo, una clase para probar que un campo de modelo está validado correctamente, con funciones para probar cada uno de los posibles casos de falla). 
# Una vez más, la estructura depende en gran medida de usted, pero es mejor si es coherente.

# Para escribir una prueba, se deriva de cualquiera de las clases base de prueba de Django (o unittest)(SimpleTestCase, TransactionTestCase, TestCase, LiveServerTestCase) 
# y luego escribir métodos separados para verificar que la funcionalidad específica funcione como se esperaba (las pruebas usan métodos "assert" para probar que las expresiones dan valores True o False, o que dos valores son iguales, etc.) 
# Cuando inicia una ejecución de prueba, el marco ejecuta los métodos de prueba elegidos en sus clases derivadas. 

class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        # setUpTestData() se llama una vez al comienzo de la ejecución de prueba para la configuración a nivel de clase. Usaría esto para crear objetos que no se modificarán ni cambiarán en ninguno de los métodos de prueba.
        print("setUpTestData: Ejecute una vez para configurar datos no modificados para todos los métodos de clase.")
        pass

    def setUp(self):
        # setUp() se llama antes de cada función de prueba para configurar cualquier objeto que pueda ser modificado por la prueba (cada función de prueba obtendrá una copia "nueva" de estos objetos).
        print("setUp: Ejecutar una vez por cada método de prueba para configurar datos limpios.")
        pass

    # estos serán métodos de prueba, que utilizamos funciones Assert toprobar si las condiciones son verdaderas, falsas o iguales (AssertTrue, AssertFalse, AssertEqual). 
    # Si la condición no se evalúa como se esperaba, la prueba fallará y reportará el error a su consola.

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)

    # Los AssertTrue, AssertFalse, AssertEqual son afirmaciones estándar proporcionadas por unittest. 
    # Hay otras aserciones estándar en el marco y también aserciones específicas de Django (Django-specific assertions) para probar si una vista redirecciona (assertRedirects),para probar si se ha utilizado una plantilla en particular (assertTemplateUsed), etc.

# para ejecutar pruebas: python manage.py test
# Si desea ejecutar un subconjunto de sus pruebas, puede hacerlo especificando la ruta de puntos completa al paquete (s), módulo, TestCase subclase o metodo:
        
# python manage.py test catalog.tests   # Ejecutar el módulo especificado
# python manage.py test catalog.tests.test_models  # Ejecutar el submódulo especificado
# python manage.py test catalog.tests.test_models.YourTestClass # Ejecutar la clase especificada
# python manage.py test catalog.tests.test_models.YourTestClass.test_one_plus_one_equals_two  # Ejecutar el método especificado