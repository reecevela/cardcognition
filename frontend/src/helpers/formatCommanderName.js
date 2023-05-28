const formatCommanderName = (name) => {
    let formattedName = name.split(' // ')[0];
    if (formattedName.startsWith('A-')) {
        formattedName = formattedName.slice(2);
    }
    formattedName = formattedName.replace(/\s/g, '-');
    formattedName = formattedName.toLowerCase().replace(/[\s,"'.\u200B]/g, '');
    return formattedName;
};

export default formatCommanderName;