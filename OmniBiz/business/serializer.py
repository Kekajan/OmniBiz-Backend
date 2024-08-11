# serializers.py
import logging
import os
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers

from Utils.Database.Database_Routing.add_database import add_database
from Utils.Database.Generate_Database.Dynamic_Database import DynamicDatabaseCreationCommand
from business.models import Business
from cash_book.views import create_cash_book_entry
from owner.models import Owner


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = [
            'business_id', 'owner', 'created_at', 'daily_revenue',
            'subscription_trial_ended_at', 'subscription_amount',
            'subscription_started_at', 'subscription_ended_at',
            'subscription_count', 'is_active'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        now = timezone.now()

        if not user.is_staff:
            validated_data['subscription_trial_ended_at'] = now + timedelta(days=90)
            validated_data['subscription_amount'] = 5000
            validated_data['subscription_started_at'] = None
            validated_data['subscription_ended_at'] = None
            validated_data['subscription_count'] = 0
            validated_data['is_active'] = True
            business = Business(owner=user, **validated_data)
            business.save()

            business_id = business.business_id

            database_command = DynamicDatabaseCreationCommand()
            try:
                logging.info("Database Creation Process started serializers")
                result = database_command.create_and_migrate_dynamic_db(business_id=business_id)
                logging.info("Database Creation Process finished serializers")
            except Exception as e:
                logging.info("Database process not inintialized due to an error serializers")
                business.delete()
                raise serializers.ValidationError(f"Business creation failed due to database error: {str(e)}")

            if not result:
                business.delete()
                raise serializers.ValidationError("Business creation failed due to database error.")
            else:
                try:
                    owner = Owner.objects.get(user_id=user.user_id)
                    logging.info(f"owner user_id : {user.user_id}")
                    logging.info(f"owner : {owner}")
                    owner.business_count += 1
                    owner.save()
                    try:
                        business_id = business.business_id
                        cash_book_data = {
                            'business_id': business_id,
                            'transaction_amount': business.initial,
                            'transaction_type': 'income',
                            'description': 'Initial amount while create business',
                            'created_by': user.user_id,
                        }
                        result = create_cash_book_entry(cash_book_data)
                        if result.status_code == 201:
                            logging.info("Cashbook Data successfully loaded serializers")
                            return business
                        else:
                            logging.info("Error While creating initial entry")
                            return 'Error While creating initial entry'
                    except Exception as e:
                        logging.info("Error while try to increase the business count")
                        raise serializers.ValidationError(f"Error creating initial entry: {str(e)}")

                except Exception as e:
                    raise serializers.ValidationError(
                        f"Error while increase the business count in owner table : {str(e)}")
        else:
            raise serializers.ValidationError("You are not allowed to create business.")
