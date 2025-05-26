from rest_framework import serializers
from .models import User, UserPreference

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""
    class Meta:
        model = UserPreference
        fields = ['id', 'learning_pace', 'preferred_content_type', 'notification_preferences',
                  'study_reminder_time', 'visual_preference', 'auditory_preference',
                  'reading_preference', 'kinesthetic_preference']
        
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user accounts"""
    preferences = UserPreferenceSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                 'bio', 'profile_picture', 'date_of_birth', 'phone_number', 'address',
                 'preferred_language', 'experience_points', 'level', 'streak_days',
                 'last_activity_date', 'linkedin_profile', 'github_profile', 'website',
                 'preferences', 'password', 'is_active', 'date_joined']
        read_only_fields = ['id', 'experience_points', 'level', 'streak_days', 'is_active', 'date_joined']
        
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        # Create default preferences
        UserPreference.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        """Update user, setting the password correctly"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user
