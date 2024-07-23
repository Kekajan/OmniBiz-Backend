import string
from random import choice


class RandomId:
    @staticmethod
    def generate_id(model_instance, field_name, size, using=None):
        model_class = model_instance.__class__
        characters = string.ascii_lowercase + string.digits
        while True:
            generated_id = ''.join(choice(characters) for _ in range(size))
            filter_kwargs = {field_name: generated_id}
            if not model_class.objects.using(using).filter(**{field_name: generated_id}).exists():
                break
        return generated_id
