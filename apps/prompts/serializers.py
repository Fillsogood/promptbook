from rest_framework import serializers

from .models import Prompt, PromptLog, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class PromptSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), write_only=True, source="tags")

    class Meta:
        model = Prompt
        fields = [
            "id",
            "title",
            "content",
            "is_public",
            "is_favorite",
            "tags",
            "tag_ids",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        prompt = Prompt.objects.create(**validated_data)
        prompt.tags.set(tags)
        return prompt

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class PromptLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptLog
        fields = [
            "id",
            "prompt",
            "input_text",
            "output_text",
            "created_at",
        ]
        read_only_fields = ["id", "output_text", "created_at", "prompt"]
