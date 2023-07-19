from flask_assets import Bundle

bundles = {
    'home_css': Bundle(
        'css/normalize.css',
        'scss/main.scss',
        filters='libsass',
        depends='scss/*.scss',
        output='gen/home.%(version)s.css'
    ),
    'home_js': Bundle(
        'js/alpine.js',
        'js/main.js',
        filters='jsmin',
        output='gen/home.%(version)s.js'
    )
}