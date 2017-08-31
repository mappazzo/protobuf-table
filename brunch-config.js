module.exports = {
  files: {
    javascripts: {
      entryPoints: {
        'src/pbTable.js': 'pbTable_package.js'
      }
    }
  },
  paths: {
    public: 'build',
    watched: ['src']
  },
  plugins: {
    babel: {presets: ['env']},
    uglify: {
      mangle: false,
      compress: true
    }
  }
}
