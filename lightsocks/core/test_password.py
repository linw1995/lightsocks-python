import unittest
import random
import base64

from lightsocks.core.password import (IDENTITY_PASSWORD, randomPassword,
                                      validatePassword, loadsPassword,
                                      dumpsPassword, InvalidPasswordError)


class TestCipher(unittest.TestCase):
    def test_randomPassword(self):
        for idx in range(0xff):
            with self.subTest(idx):
                password = randomPassword()
                isValid = validatePassword(password)
                self.assertTrue(isValid)

    def test_dumps_and_loads_succeed(self):
        password = randomPassword()

        string = dumpsPassword(password)

        loaded_password = loadsPassword(string)

        self.assertEqual(password, loaded_password)

    def test_dumps_and_loads_fail(self):
        password = randomPassword()
        password[random.randint(1, 255)] = 0

        with self.assertRaises(InvalidPasswordError):
            dumpsPassword(password)

        string = base64.encodebytes(password).decode('utf8', errors='strict')

        with self.assertRaises(InvalidPasswordError):
            loadsPassword(string)

        password = randomPassword()
        password = password[:-2]

        with self.assertRaises(InvalidPasswordError):
            dumpsPassword(password)

        string = dumpsPassword(IDENTITY_PASSWORD)
        string = string[:-3]

        with self.assertRaises(InvalidPasswordError):
            loadsPassword(string)
