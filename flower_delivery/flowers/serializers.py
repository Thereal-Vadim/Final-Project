from rest_framework import serializers
from .models import Order, OrderItem, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ['user', 'products', 'delivery_address', 'status', 'created_at']

    def create(self, validated_data):
        order_items_data = validated_data.pop('orderitem_set')
        order = Order.objects.create(user=validated_data['user'], delivery_address=validated_data['delivery_address'], status=validated_data['status'])
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, product=item_data['product'], quantity=item_data['quantity'])
        return order