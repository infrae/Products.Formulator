import unittest
import Zope
from Products.Formulator import Validator


class TestField:
    def __init__(self, id, **kw):
        self.id = id
        self.kw = kw

    def get_value(self, name):
        return self.kw[name]

    def get_error_message(self, key):
        return "nothing"

class ValidatorTestCase(unittest.TestCase):
    def assertValidatorRaises(self, exception, error_key, f, *args, **kw):
        try:
            apply(f, args, kw)
        except Validator.ValidationError, e:
            if e.error_key != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)

class StringValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.StringValidatorInstance

    def tearDown(self):
        pass
        
    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0),
            'f', {'f' : 'foo'})
        self.assertEqual('foo', result)

    def test_strip_whitespace(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0),
            'f', {'f' : ' foo  '})
        self.assertEqual('foo', result)

    def test_error_too_long(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=10, truncate=0, required=0),
            'f', {'f' : 'this is way too long'})
        
    def test_error_truncate(self):
        result = self.v.validate(
            TestField('f', max_length=10, truncate=1, required=0),
            'f', {'f' : 'this is way too long'})
        self.assertEqual('this is way too long'[:10], result)

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {})
        
class EmailValidatorTestCase(ValidatorTestCase):
     
    def setUp(self):
        self.v = Validator.EmailValidatorInstance
        
    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': 'foo@bar.com'})
        self.assertEquals('foo@bar.com', result)
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': 'm.faassen@vet.uu.nl'})
        self.assertEquals('m.faassen@vet.uu.nl', result) 

    def test_error_not_email(self):
        # a few wrong email addresses should raise error
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': 'foo@bar.com.'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': '@bar.com'})
        
    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': ''})
        
def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(StringValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailValidatorTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
