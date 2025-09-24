export const extractSkills = (text) => {
  const skillKeywords = [
    "Java", "Python", "C++", "React", "Node.js", "MongoDB",
    "SQL", "HTML", "CSS", "Express", "Machine Learning",
  ];
  return skillKeywords.filter((skill) =>
    text.toLowerCase().includes(skill.toLowerCase())
  );
};