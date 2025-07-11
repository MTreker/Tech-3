from django.test import TestCase
from django.urls import reverse
from .models import Item
from .forms import ItemForm

class ItemModelTest(TestCase):
    def test_create_item(self):
        item = Item.objects.create(name='Test Item', description='A test description')
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.description, 'A test description')
        self.assertTrue(isinstance(item, Item))

class ItemFormTest(TestCase):
    def test_valid_form(self):
        data = {'name': 'Valid Name', 'description': 'Valid description'}
        form = ItemForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'name': '', 'description': 'Missing name'}
        form = ItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

class ItemViewTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(name='Existing Item', description='Existing description')

    def test_item_list_view(self):
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_list.html')
        self.assertContains(response, self.item.name)

    def test_item_create_view_get(self):
        response = self.client.get(reverse('item_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_form.html')

    def test_item_create_view_post_valid(self):
        data = {'name': 'New Item', 'description': 'New description'}
        response = self.client.post(reverse('item_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(name='New Item').exists())

    def test_item_create_view_post_invalid(self):
        initial_count = Item.objects.count()
        data = {'name': '', 'description': 'No name provided'}
        response = self.client.post(reverse('item_create'), data)
        # Expect the form to re-render with errors (status 200)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form, "Form not found in response context")
        self.assertTrue(form.errors)
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])
        # Ensure no new item was created
        self.assertEqual(Item.objects.count(), initial_count)

    def test_item_update_view_get(self):
        response = self.client.get(reverse('item_update', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_form.html')

    def test_item_update_view_post_valid(self):
        data = {'name': 'Updated Item', 'description': 'Updated description'}
        response = self.client.post(reverse('item_update', args=[self.item.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Item')

    def test_item_delete_view_get(self):
        response = self.client.get(reverse('item_delete', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_confirm_delete.html')

    def test_item_delete_view_post(self):
        response = self.client.post(reverse('item_delete', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())
