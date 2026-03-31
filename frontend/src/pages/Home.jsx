/**
 * Home page — simple landing page for the CRUD template.
 *
 * Displays the application name, description, and links to each
 * registered resource.  When creating a new application, customize
 * this page to fit your domain.
 */

import { Link } from "react-router-dom";
import { resources, appConfig } from "../config/resources";

export default function Home() {
  const sorted = [...resources].sort((a, b) => a.navOrder - b.navOrder);

  return (
    <div className="home">
      <h1>{appConfig.name}</h1>
      <p>{appConfig.description}</p>

      <div className="home-cards">
        {sorted.map((resource) => (
          <Link
            key={resource.name}
            to={`/${resource.name}`}
            className="home-card"
          >
            <h2>{resource.label}</h2>
            <p>Manage {resource.label.toLowerCase()}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
