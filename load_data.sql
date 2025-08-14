\COPY providers FROM 'C:/Users/Anuradha/Food_Donation/clean_providers.csv' DELIMITER ',' CSV HEADER;
\COPY receivers FROM 'C:/Users/Anuradha/Food_Donation/clean_receivers.csv' DELIMITER ',' CSV HEADER;
\COPY food_listings FROM 'C:/Users/Anuradha/Food_Donation/clean_food_listings.csv' DELIMITER ',' CSV HEADER;
\COPY claims FROM 'C:/Users/Anuradha/Food_Donation/clean_claims.csv' DELIMITER ',' CSV HEADER;