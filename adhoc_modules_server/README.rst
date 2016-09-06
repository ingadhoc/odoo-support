TODO
====
1. Agregar un token de github en ""

## Pendientes:

* TODO ver si las categorias invisibles es practico que sean visibles para admin

* Podriamos simplificar la integracion usando el modulo que permite importar no por id si no por otros campo, entonces usariamos "name" e id de categoria

* Vincular documentos o temas a un módulo para que luego de instalarlo al client lo lleve a la documentación correspondiente

* Si el auto refresh con wizard desde kanban no nos gusta, podemos ver esto https://github.com/szufisher/web/tree/8.0/web_auto_refresh

* Agregar campo calculado en modulos de adhoc "also available for", que busque otro modulo con mismo nombre. También que deje, con un boton, copiar data de los otros modulos (mezclando todos los datos que existan), que dicha acción se pueda correr tambien desde la vist lista de modulos.

* al cancelar una instalación de un modulo, mostrar los módulos que van a dejar de ser instalados también porque requerian a este (parecido a lo que hacemos al instalar)

* Agregar version requerida en los modulos o algo por el estilo para que se actualice automáticamente (vamos a ver si en realidad lo manejamos de otra manera lo de actualizar a todo el mundo)

    
## Pendientes low priority:
* Evaluar si es mejor entrar a la kanban de categorías con un default_group_by="parent_id" para que permita drag and drop y de un solo vistazo vez todas las categorías, tipo dashboard.
* implementar suggested subcategories
* Sacar warning de "InsecurePlatformWarning: A true SSLContext object is not available."
