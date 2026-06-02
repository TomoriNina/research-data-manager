CREATE DATABASE IF NOT EXISTS `research_data` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE research_data;

CREATE TABLE IF NOT EXISTS `projects` (
    `project_id` int NOT NULL AUTO_INCREMENT COMMENT '课题ID',
    `project_name` varchar(100) NOT NULL COMMENT '课题名称',
    `researcher` varchar(100) NOT NULL COMMENT '课题负责人',
    `create_date` date DEFAULT(curdate()) COMMENT '课题创建日期',
    `remark` text COMMENT '课题备注',
    PRIMARY KEY (`project_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '科研课题表';

CREATE TABLE IF NOT EXISTS `experiment_batches` (
    `batch_id` int NOT NULL AUTO_INCREMENT COMMENT '批次ID',
    `batch_name` varchar(100) NOT NULL COMMENT '批次名称',
    `project_id` int NOT NULL COMMENT '所属课题ID',
    `experiment_date` date DEFAULT(curdate()) COMMENT '实验日期',
    `remark` text COMMENT '实验备注',
    PRIMARY KEY (`batch_id`),
    KEY `fk_experiment_batches_projects` (`project_id`),
    CONSTRAINT `fk_experiment_batches_projects` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '实验批次表';

CREATE TABLE IF NOT EXISTS `experiment_params` (
    `param_id` int NOT NULL AUTO_INCREMENT COMMENT '参数ID',
    `param_name` varchar(50) NOT NULL COMMENT '参数名称',
    `param_value` varchar(50) NOT NULL COMMENT '参数值',
    `batch_id` int NOT NULL COMMENT '批次ID',
    PRIMARY KEY (`param_id`),
    KEY `fk_experiment_params_experiment_batches` (`batch_id`),
    CONSTRAINT `fk_experiment_params_experiment_batches` FOREIGN KEY (`batch_id`) REFERENCES `experiment_batches` (`batch_id`) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '实验参数表';

CREATE TABLE IF NOT EXISTS `data_files` (
    `file_id` int NOT NULL AUTO_INCREMENT COMMENT '文件ID',
    `file_name` varchar(100) NOT NULL COMMENT '文件名',
    `file_path` text NOT NULL COMMENT '文件路径',
    `version` int DEFAULT NULL COMMENT '版本',
    `batch_id` int NOT NULL COMMENT '批次ID',
    PRIMARY KEY (`file_id`),
    KEY `fk_data_files_experiment_batches` (`batch_id`),
    CONSTRAINT `fk_data_files_experiment_batches` FOREIGN KEY (`batch_id`) REFERENCES `experiment_batches` (`batch_id`) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '实验数据文件表';