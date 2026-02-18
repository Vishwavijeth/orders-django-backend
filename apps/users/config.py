from djchoices import DjangoChoices, ChoiceItem

class RoleTypeChoices(DjangoChoices):
    admin = ChoiceItem('admin', 'Admin')
    customer = ChoiceItem('customer', 'Customer')
    restaurant_admin = ChoiceItem('restaurant_admin', 'Restaurant_admin')