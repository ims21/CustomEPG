from distutils.core import setup
import setup_translate

pkg = 'Extensions.TimerPlanner'
setup (name = 'enigma2-plugin-extensions-timerplanner',
	version = '1.02',
	description = 'Timer planner for selected services',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['*.png', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
	cmdclass = setup_translate.cmdclass, # for translation
	)
