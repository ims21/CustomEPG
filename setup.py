from distutils.core import setup
import setup_translate

pkg = 'Extensions.CustomEPG'
setup (name = 'enigma2-plugin-extensions-customepg',
	version = '0.7',
	description = 'EPG for selected services',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['*.png', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
	cmdclass = setup_translate.cmdclass, # for translation
	)
