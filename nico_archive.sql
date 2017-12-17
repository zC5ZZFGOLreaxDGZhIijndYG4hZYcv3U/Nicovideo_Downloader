-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Dec 17, 2017 at 02:23 PM
-- Server version: 5.7.18-0ubuntu0.16.04.1
-- PHP Version: 7.0.18-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `nico_archive`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_dl_stack`
--

CREATE TABLE `auth_dl_stack` (
  `author_id` varchar(30) CHARACTER SET utf8 NOT NULL,
  `video_ID` varchar(30) CHARACTER SET utf8 NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `delVideos`
--

CREATE TABLE `delVideos` (
  `video_ID` varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `erroneous_dls`
--

CREATE TABLE `erroneous_dls` (
  `video_ID` varchar(40) CHARACTER SET utf8 NOT NULL,
  `new_filename` varchar(40) CHARACTER SET utf8 NOT NULL,
  `ffmpeg_stderr` text CHARACTER SET utf8 NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `nicovideo`
--

CREATE TABLE `nicovideo` (
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `video_ID` varchar(11) CHARACTER SET utf8 NOT NULL,
  `download_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `upload_date` datetime NOT NULL,
  `uploader` text CHARACTER SET utf8 NOT NULL,
  `mylists` int(11) NOT NULL,
  `comments` int(11) NOT NULL,
  `views` int(11) NOT NULL,
  `method` text CHARACTER SET utf8 NOT NULL,
  `uploader_name` text CHARACTER SET utf8 NOT NULL,
  `downloaded` tinyint(1) NOT NULL,
  `isLowQual` bit(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `nicovideo_file_migrations`
--

CREATE TABLE `nicovideo_file_migrations` (
  `original_file_location` varchar(200) CHARACTER SET utf8 NOT NULL,
  `destination_file_location` varchar(200) CHARACTER SET utf8 NOT NULL,
  `time_stamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `nicovideo_users`
--

CREATE TABLE `nicovideo_users` (
  `user_ID` int(11) NOT NULL,
  `name` text CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `nico_tags`
--

CREATE TABLE `nico_tags` (
  `video_ID` varchar(12) CHARACTER SET utf8 NOT NULL,
  `tag` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `tag_dl_stack`
--

CREATE TABLE `tag_dl_stack` (
  `video_ID` varchar(30) CHARACTER SET utf8 NOT NULL,
  `Upload_Date` date NOT NULL,
  `Tag` varchar(30) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_dl_stack`
--
ALTER TABLE `auth_dl_stack`
  ADD PRIMARY KEY (`video_ID`);

--
-- Indexes for table `delVideos`
--
ALTER TABLE `delVideos`
  ADD PRIMARY KEY (`video_ID`);

--
-- Indexes for table `erroneous_dls`
--
ALTER TABLE `erroneous_dls`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `nicovideo`
--
ALTER TABLE `nicovideo`
  ADD PRIMARY KEY (`video_ID`),
  ADD UNIQUE KEY `video_ID` (`video_ID`);

--
-- Indexes for table `nicovideo_file_migrations`
--
ALTER TABLE `nicovideo_file_migrations`
  ADD PRIMARY KEY (`original_file_location`);

--
-- Indexes for table `nicovideo_users`
--
ALTER TABLE `nicovideo_users`
  ADD PRIMARY KEY (`user_ID`),
  ADD UNIQUE KEY `user_ID` (`user_ID`);

--
-- Indexes for table `nico_tags`
--
ALTER TABLE `nico_tags`
  ADD PRIMARY KEY (`video_ID`,`tag`),
  ADD KEY `tag` (`tag`);

--
-- Indexes for table `tag_dl_stack`
--
ALTER TABLE `tag_dl_stack`
  ADD PRIMARY KEY (`video_ID`,`Tag`),
  ADD KEY `Tag` (`Tag`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `erroneous_dls`
--
ALTER TABLE `erroneous_dls`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
