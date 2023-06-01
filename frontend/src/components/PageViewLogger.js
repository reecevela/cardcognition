import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { logEvent } from 'firebase/analytics';
import { analytics } from '../index';

function PageViewLogger() {
  const location = useLocation();

  useEffect(() => {
    logEvent(analytics, 'page_view', {
      page_path: location.pathname,
      time: new Date().toString()
    });
  }, [location]);

  return null;
}

export default PageViewLogger;
