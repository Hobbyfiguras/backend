class MinimalPostSerializer(serializers.ModelSerializer):
    creator = MinimalUserSerializer()
    thread = ThreadSerializer()

    class Meta:
        model = Post
        exclude = ('content',)

class PostSerializer(serializers.ModelSerializer):
    creator = PublicUserSerializer()

    class Meta:
        model = Post
        fields = '__all__'