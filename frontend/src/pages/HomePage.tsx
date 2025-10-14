import { useTranslation } from 'react-i18next';

const HomePage = () => {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 font-sans">
      <header className="bg-white shadow-sm">
        <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <a href="/" className="text-2xl font-bold text-gray-800">
              {t('header.logoText')}
            </a>
          </div>
          <div className="flex space-x-6">
            <a href="#" className="text-gray-600 hover:text-blue-600">{t('header.nav.home')}</a>
            <a href="#" className="text-gray-600 hover:text-blue-600">{t('header.nav.about')}</a>
            <a href="#" className="text-gray-600 hover:text-blue-600">{t('header.nav.contact')}</a>
          </div>
        </nav>
      </header>

      <main className="flex-grow container mx-auto px-6 py-20 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-4">
            {t('main.title')}
          </h1>
          <p className="text-lg text-gray-700 mb-8 max-w-2xl mx-auto">
            {t('main.subtitle')}
          </p>
          <button className="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-300">
            {t('main.ctaButton')}
          </button>
        </div>
      </main>

      <footer className="bg-white mt-auto">
        <div className="container mx-auto px-6 py-4 text-center text-gray-500">
          <p>&copy; {new Date().getFullYear()} {t('footer.copyright')}</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;