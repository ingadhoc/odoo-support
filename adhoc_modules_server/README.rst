TODO
====

En clientes:
    Agregamos en categorías un campo booleano "Contratado"

En nuestra bd:
    los productos tienen un link a "categoría de módulos"
    Entonces al agregar un producto a una bd, se actualiza la bd del cliente seteando que esa categoría está comprada.

    
* Evaluar si es mejor entrar a la kanban de categorías con un default_group_by="parent_id" para que permita drag and drop y de un solo vistazo vez todas las categorías, tipo dashboard.
* implementar suggested subcategories
* Agregar modules required para categorías? y que solo aparezcan si dichos modulos estan instalados)
* Agregamos atributos a los módulos tipo sugerido, normal, skipped. Luego en las kanban de categorías, si no hay ninguno a revisar (todos skipped o instalados) lo mostramos de un color, como para saber que terminaste una configuración
* De hecho solo mostramos de manera predeterminada (por filtro) categorías recomendadas y módulos a revisae
* Implementar sacar descripciones de readme o index, tampoco es tan necesario
* agregar vista particular para configuracion que muestre los desconfigurados
* mejorar button_install_cancel para que desmarque los padres
* Llevar todo lo que podamos al modulo de clientes, y luego que este dependa de aquel

* Vincular documentos o temas a un módulo para que luego de instalarlo al client lo lleve a la documentación correspondiente
* Traer icono, aunque es renigue sin sentido tal vez
* Agregar version requerida en los modulos o algo por el estilo para que se actualice automáticamente
* Cron para actualizar repos (solo los auto_update)
* Mostrar los que faltan asignar
* Sacar warning de "InsecurePlatformWarning: A true SSLContext object is not available."
