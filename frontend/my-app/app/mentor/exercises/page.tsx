'use client';

import Exercise from "../components/Exercise";

const ExercisesPage = () => {
  return (
    <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Exercises</h1>
        <div className="grid grid-cols-1 gap-4">
            <Exercise title="Exercise 1" category="Math" submissions="5 submissions" />
            <Exercise title="Exercise 2" category="Science" submissions="3 submissions" />
            <Exercise title="Exercise 3" category="History" submissions="8 submissions" />
        </div>
    </div>
  );
}

export default ExercisesPage;