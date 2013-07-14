BEGIN;

CREATE TABLE concision_queries (
    "id" SERIAL NOT NULL,
    "name" VARCHAR NOT NULL,
    data TEXT NOT NULL,
    
    complete BOOLEAN NOT NULL DEFAULT FALSE,
    
    "creator" INTEGER NOT NULL,
    
    PRIMARY KEY ("id"),
    FOREIGN KEY("creator") REFERENCES users (id)
);
-- CREATE INDEX ix_connect_four_profiles_user ON connect_four_profiles ("user");

CREATE TABLE concision_reports (
    "id" SERIAL NOT NULL,
    "name" VARCHAR NOT NULL,
    
    data TEXT NOT NULL,
    "creator" INTEGER NOT NULL,
    
    PRIMARY KEY ("id"),
    FOREIGN KEY("creator") REFERENCES users (id)
);

COMMIT;
